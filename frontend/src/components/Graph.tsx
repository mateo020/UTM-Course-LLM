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

const H_GAP = 200;   /* horizontal distance between columns  */
const V_GAP = 70;    /* vertical distance between rows      */

export const Graph: React.FC<GraphProps> = ({ focusId, graphUrl }) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [error, setError] = useState<string | null>(null);

  /* highlight‑selection state */
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [ancestors, setAncestors] = useState<Set<string>>(new Set());
  const [descendants, setDescendants] = useState<Set<string>>(new Set());

  const id2node = (arr: Node[]) => Object.fromEntries(arr.map(n => [n.id, n]));

  /* --------------- fetch + deterministic layout --------------- */
  useEffect(() => {
    if (!focusId) return;

    (async () => {
      try {
        const { data } = await axios.get(`${graphUrl}/${focusId}`);
        const rawNodes: Node[] = data.nodes.map((n: any) => ({ ...n, label: n.id }));
        const rawEdges: Edge[] = data.links || [];

        const dict = id2node(rawNodes);
        const nextRowForX: Record<number, number> = { 0: 0 }; // track y‑offset per column

        const enqueue = (id: string, x: number) => {
          const n = dict[id];
          if (n && n.fx === undefined) {
            n.fx = x;
            n.fy = nextRowForX[x] ?? 0;
            nextRowForX[x] = (nextRowForX[x] ?? 0) + V_GAP;
            queue.push(id);
          }
        };

        /* BFS walk setting deterministic positions */
        const queue: string[] = [];
        dict[focusId].fx = 0;
        dict[focusId].fy = 0;
        queue.push(focusId);

        while (queue.length) {
          const curId = queue.shift()!;
          const curX  = dict[curId].fx ?? 0;

          // outgoing children  -> right column
          rawEdges.filter(e => e.source === curId).forEach(e => enqueue(e.target as string, curX + H_GAP));

          // incoming parents   -> left column
          rawEdges.filter(e => e.target === curId).forEach(e => enqueue(e.source as string, curX - H_GAP));
        }

        setNodes(rawNodes);
        setEdges(rawEdges);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unexpected error');
      }
    })();
  }, [focusId, graphUrl]);

  /* derive highlight sets when user clicks */
  useEffect(() => {
    if (!selectedId) { setAncestors(new Set()); setDescendants(new Set()); return; }

    const up = new Set<string>();
    const down = new Set<string>();
    const upStack   = [selectedId];
    const downStack = [selectedId];

    while (upStack.length) {
      const cur = upStack.pop()!;
      edges.filter(e => e.target === cur).forEach(e => { if (!up.has(e.source)) { up.add(e.source); upStack.push(e.source); } });
    }
    while (downStack.length) {
      const cur = downStack.pop()!;
      edges.filter(e => e.source === cur).forEach(e => { if (!down.has(e.target)) { down.add(e.target); downStack.push(e.target); } });
    }
    setAncestors(up); setDescendants(down);
  }, [selectedId, edges]);

  if (error) return <div className="text-red-600 p-4">Error: {error}</div>;
  if (nodes.length === 0) return <div className="text-gray-600 p-4">Loading…</div>;

  /* ------------- colour + width helpers ------------- */
  const nodeFill = (n: Node) => {
    if (!selectedId) return n.id === focusId ? '#4F46E5' : '#60A5FA';
    if (n.id === selectedId) return '#ef4444';
    if (ancestors.has(n.id)) return '#0ea5e9';
    if (descendants.has(n.id)) return '#4F46E5';
    return '#d1d5db';
  };

  const linkFill = (l: Edge) => {
    const s = typeof l.source === 'object' ? (l.source as any).id : l.source;
    const t = typeof l.target === 'object' ? (l.target as any).id : l.target;
    if (!selectedId) return s === focusId ? '#4F46E5' : '#94A3B8';
    if (s === selectedId || t === selectedId) return '#ef4444';
    if (ancestors.has(s) && ancestors.has(t)) return '#0ea5e9';
    if (descendants.has(s) && descendants.has(t)) return '#4F46E5';
    return '#d1d5db';
  };

  const linkWidth = (l: Edge) => (linkFill(l) === '#d1d5db' ? 1 : 3);

  return (
    <div className="graph-container">
      <ForceGraph2D
        graphData={{ nodes, links: edges }}
        backgroundColor="#F8FAFC"
        width={800}
        height={600}
        nodeLabel="label"
        linkLabel="label"
        nodeColor={nodeFill}
        linkColor={linkFill}
        nodeRelSize={6}
        linkWidth={linkWidth}
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0.25}
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.004}
        onNodeClick={(n: any) => setSelectedId(prev => (prev === n.id ? null : n.id))}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          const label = node.label;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.fillStyle = nodeFill(node);
          ctx.beginPath();
          ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI);
          ctx.fill();
          ctx.fillStyle = '#374151';
          ctx.textAlign = 'center';
          ctx.fillText(label, node.x, node.y + 10);
        }}
      />
      <div className="graph-legend mt-2 text-sm">
        <p>Nodes: {nodes.length} • Edges: {edges.length}</p>
        {selectedId && (
          <p>
            Selected <span className="font-semibold">{selectedId}</span> — Ancestors: {ancestors.size} • Descendants: {descendants.size}
          </p>
        )}
      </div>
    </div>
  );
};
