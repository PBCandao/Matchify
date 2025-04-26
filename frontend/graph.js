window.addEventListener('load', () => {
  fetch('/graph?user=alice&depth=1')
    .then(res => {
      if (!res.ok) throw new Error(res.statusText);
      return res.json();
    })
    .then(data => {
      drawGraph(data.nodes, data.links);
    })
    .catch(err => console.error('Error loading graph data:', err));
});

function drawGraph(nodes, links) {
  let container = document.getElementById('graph-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'graph-container';
    document.body.appendChild(container);
  }
  container.innerHTML = '';
  const width = container.clientWidth || window.innerWidth;
  const height = container.clientHeight || window.innerHeight;
  if (typeof d3 !== 'undefined') {
    const svg = d3.select(container).append('svg')
      .attr('width', width)
      .attr('height', height);
    const link = svg.append('g').selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 1);
    const node = svg.append('g').selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('r', 10)
      .attr('fill', '#69b3a2');
    const label = svg.append('g').selectAll('text')
      .data(nodes)
      .enter().append('text')
      .text(d => d.id)
      .attr('font-size', 10)
      .attr('dx', 12)
      .attr('dy', 4);
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-200))
      .force('center', d3.forceCenter(width / 2, height / 2));
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });
  } else {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    container.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    nodes.forEach(n => {
      n.x = Math.random() * width;
      n.y = Math.random() * height;
    });
    ctx.strokeStyle = '#999';
    links.forEach(l => {
      const s = nodes.find(n => n.id === l.source);
      const t = nodes.find(n => n.id === l.target);
      if (s && t) {
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.stroke();
      }
    });
    ctx.fillStyle = '#69b3a2';
    nodes.forEach(n => {
      ctx.beginPath();
      ctx.arc(n.x, n.y, 10, 0, 2 * Math.PI);
      ctx.fill();
      ctx.fillStyle = '#000';
      ctx.fillText(n.id, n.x + 12, n.y + 4);
      ctx.fillStyle = '#69b3a2';
    });
  }
}
