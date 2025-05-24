import React, { useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';

interface Node {
  id: string;
  label: string;
  fx?: number;
  fy?: number;
}

interface Edge {
  source: string;
  target: string;
  label: string;
}

type GraphProps = {
  focusId?: string;
  graphUrl: string;
};

const H_GAP = 200; // horizontal gap between columns

export const Graph: React.FC<GraphProps> = ({ focusId, graphUrl }) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [error, setError] = useState<string | null>(null);

  // helper to build lookup
  const id2node = (arr: Node[]) => Object.fromEntries(arr.map(n => [n.id, n]));

  /* ---------- load & position graph ---------- */
  useEffect(() => {
    if (!focusId) return;

    const fetchGraphData = async () => {
      try {
        const { data } = await axios.get(`${graphUrl}/${focusId}`);
        const rawNodes: Node[] = data.nodes.map((n: any) => ({ ...n, label: n.id }));
        const rawEdges: Edge[] = data.links || [];

        /* ---- BFS-style positioning ---- */
        const dict = id2node(rawNodes);
        const queue: string[] = [focusId];
        dict[focusId].fx = 0; // centre
        dict[focusId].fy = 0;

        while (queue.length) {
          const currentId = queue.shift()!;
          const cur = dict[currentId];

          // outgoing: current -> child  => place child to the right
          rawEdges.filter(e => e.source === currentId).forEach(e => {
            const child = dict[e.target];
            if (child && child.fx === undefined) {
              child.fx = (cur.fx ?? 0) + H_GAP;
              child.fy = (Math.random() - 0.5) * 400;
              queue.push(child.id);
            }
          });

          // incoming: parent -> current  => place parent to the left
          rawEdges.filter(e => e.target === currentId).forEach(e => {
            const parent = dict[e.source];
            if (parent && parent.fx === undefined) {
              parent.fx = (cur.fx ?? 0) - H_GAP;
              parent.fy = (Math.random() - 0.5) * 400;
              queue.push(parent.id);
            }
          });
        }

        setNodes(rawNodes);
        setEdges(rawEdges);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unexpected error');
      }
    };

    fetchGraphData();
  }, [focusId, graphUrl]);

  if (error) return <div className="text-red-600 p-4">Error: {error}</div>;
  if (nodes.length === 0) return <div className="text-gray-600 p-4">Loading…</div>;

  return (
    <div className="graph-container">
      <ForceGraph2D
        graphData={{ nodes, links: edges }}
        backgroundColor="#F8FAFC"
        width={800}
        height={600}
        nodeLabel="label"
        linkLabel="label"
        nodeColor={n => (n.id === focusId ? '#4F46E5' : '#60A5FA')}
        // outgoing edges (where source is the node) => dark blue, incoming => gray
        linkColor={l => (l.source === focusId || (typeof l.source === 'object' && (l.source as Node).id === focusId) ? '#4F46E5' : '#94A3B8')}
        nodeRelSize={6}
        linkWidth={2}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0.25}
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.004}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          const label = node.label;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = node.id === focusId ? '#4F46E5' : '#60A5FA';
          ctx.beginPath();
          ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
          ctx.fill();
          ctx.fillStyle = '#374151';
          ctx.textAlign = 'center';
          ctx.fillText(label, node.x, node.y + 10);
        }}
      />
      <div className="graph-legend">
        <p>Nodes: {nodes.length}</p>
        <p>Edges: {edges.length}</p>
      </div>
    </div>
  );
};