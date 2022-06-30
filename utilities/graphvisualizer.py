def GraphVisualizer(data, ncol, nlabel, darkmode, edgevisibility, particles):
    # evaluate the boolean arguments
    if edgevisibility == True:
        lv = "//"
    else:
        lv = ""
    if particles == False:
        parts = "//"
    else:
        parts = ""
    if darkmode == False:
        dm = "//"
    else:
        dm = ""
    
    d3graph = {"nodes": [], "links": []}
    d3graph["nodes"] = data["nodes"]
    d3graph["links"] = data["links"]

    htmlcode = f"""<head>
        <style> body {{margin: 0;}} </style>
        <script src="https://unpkg.com/force-graph"></script>
        <meta charset="UTF-8">
    </head>
    <body>
    <div id="graph"></div>
    <script>
        var data = {d3graph};
        const elem = document.getElementById('graph');
        const Graph = ForceGraph()(elem)
            .graphData(data)
            .nodeLabel('{nlabel}')
            .nodeAutoColorBy('{ncol}')
            {dm}.backgroundColor('#000000')
            {dm}.linkColor(() => 'rgba(255,255,255,0.2)')
            {lv}.linkVisibility('false')
            {parts}.linkDirectionalParticles(2)
            {parts}.linkDirectionalParticleWidth(1.4)
            .onNodeClick (node => {{window.open(`https://doi.org/${{node.rel_doi}}`, '_blank')}})
            //.onNodeHover(node => elem.style.cursor = node ? 'pointer' : null)
            .onNodeRightClick(node => {{
                // Center/zoom on node
                Graph.centerAt(node.x, node.y, 1000);
                Graph.zoom(8, 2000);
            }});
    </script>
    </body>
    """
    return {'graph':htmlcode}