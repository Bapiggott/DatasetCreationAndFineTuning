public void Dijkstra(double[,] graph, int src)
{
    // Initialize distance array with infinity, indicating that initially, all distances are unknown
    double[] dist = new double[V]; // V is the number of vertices
    bool[] sptSet = new bool[V]; // Shortest path tree set, keeps track of vertices for which the shortest path is finalized

    for (int i = 0; i < V; i++)
    {
        dist[i] = double.PositiveInfinity; // Start with all distances as infinity
        sptSet[i] = false; // None of the vertices are in the shortest path tree yet
    }

    // Distance to the source from itself is always 0
    dist[src] = 0;

    // Find shortest path for all vertices
    for (int count = 0; count < V - 1; count++)
    {
        // Pick the minimum distance vertex from the set of vertices not yet processed.
        // u is always equal to src in the first iteration.
        int u = MinDistance(dist, sptSet);

        // Mark the picked vertex as processed
        sptSet[u] = true;

        // Update dist value of the adjacent vertices of the picked vertex.
        for (int v = 0; v < V; v++)
            // Update dist[v] only if it is not in sptSet, there is an edge from u to v,
            // and total weight of path from src to v through u is smaller than current value of dist[v]
            if (!sptSet[v] && graph[u, v] != double.PositiveInfinity && dist[u] != double.PositiveInfinity && dist[u] + graph[u, v] < dist[v])
                dist[v] = dist[u] + graph[u, v]; // Updating the distance
    }

    // Use the printSolution1 method to update dataGridView2 with the shortest distances from src
    printSolution1(dist, src);
}

private int MinDistance(double[] dist, bool[] sptSet)
{
    // Initialize minimum value
    double min = double.PositiveInfinity;
    int minIndex = -1;

    for (int v = 0; v < V; v++)
        if (!sptSet[v] && dist[v] <= min)
        {
            min = dist[v];
            minIndex = v;
        }

    return minIndex;
}

private void printSolution1(double[] dist, int src)
{
    // Iterating over all vertices and updating dataGridView2 with the calculated shortest distance
    // If the distance is infinity (i.e., the vertex is not reachable), display "INF"
    // Otherwise, convert the distance to an integer and display it
    for (int i = 0; i < V; ++i)
    {
        dataGridView2.Rows[src].Cells[i].Value = dist[i] == double.PositiveInfinity ? "INF" : ((int)Math.Round(dist[i])).ToString();
    }
}
