import React, { useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';
// import './Graph.css';

interface Node {
  id: string;
  label: string;
}

interface Edge {
  source: string;
  target: string;
  label: string;
}

type GraphProps = {
  focusId: string | undefined;              // ⟵ course code you care about
  graphUrl: string;              // e.g. “/data/prereq_graph.json”
};

export const Graph: React.FC<GraphProps> = ({ focusId, graphUrl }) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [error, setError] = useState<string | null>(null);
//   const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        const response = await axios.get(`${graphUrl}/${focusId}`);
        console.log('Graph data:', response.data);
        
        const withLabels = response.data.nodes.map((n: any) => ({ 
          ...n, 
          label: n.id 
        }));
        setNodes(withLabels);
        setEdges(response.data.links || []);
      } catch (e) {
        console.error('Error fetching graph data:', e);
        setError(e instanceof Error ? e.message : "Unexpected error");
      }
    };

    fetchGraphData();
  }, [focusId, graphUrl]);

    // const handleNodeClick = (node: Node) => {
    //     setSelectedNode(node);
    // };

  if (error) {
    return <div className="text-red-600 p-4">Error loading graph: {error}</div>;
  }

  if (nodes.length === 0) {
    return <div className="text-gray-600 p-4">Loading graph data...</div>;
  }

  return (
    <div className="graph-container">
      <div className="graph-wrapper">
        <ForceGraph2D
          graphData={{ nodes, links: edges }}
          nodeLabel="label"
          linkLabel="label"
          nodeColor="#4F46E5"
          linkColor="#94A3B8"
          backgroundColor="#F8FAFC"
          width={800}
          height={600}
          nodeRelSize={6}
          linkWidth={2}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          linkCurvature={0.25}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.004}
          nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
            const label = node.label;
            const fontSize = 12/globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;
            ctx.fillStyle = node.id === focusId ? '#4F46E5' : '#60A5FA';
            ctx.beginPath();
            ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
            ctx.fill();
            ctx.fillStyle = '#374151';
            ctx.textAlign = 'center';
            ctx.fillText(label, node.x, node.y + 10);
          }}
        //   onNodeClick={handleNodeClick}
        />
      </div>
      <div className="graph-legend">
        <p>Nodes: {nodes.length}</p>
        <p>Relationships: {edges.length}</p>
      </div>
    </div>
  );
}; 