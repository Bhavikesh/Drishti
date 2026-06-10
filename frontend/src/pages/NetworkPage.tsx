import React, { useState } from 'react';
import NetworkGraph from '../components/NetworkGraph';
import { networkAPI } from '../services/api';

const NetworkPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!searchTerm) return;
    setLoading(true);
    try {
      const data = await networkAPI.getGraph(undefined, searchTerm);
      setGraphData(data);
    } catch (error) {
      console.error('Failed to load network graph', error);
    }
    setLoading(false);
  };

  return (
    <div className="p-6 bg-gray-900 min-h-[calc(100vh-64px)] text-white">
      <h1 className="text-3xl font-bold mb-6">Criminal Network Analysis</h1>
      
      <div className="flex space-x-4 mb-6">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search criminal name or crime ID..."
          className="flex-1 max-w-md px-4 py-2 bg-gray-800 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSearch}
          className="px-6 py-2 bg-blue-600 rounded hover:bg-blue-700"
        >
          Analyze
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
        </div>
      ) : (
        <div className="bg-gray-800 p-4 rounded-lg shadow min-h-[600px]">
          {graphData.nodes.length > 0 ? (
            <NetworkGraph data={graphData} />
          ) : (
            <div className="flex justify-center items-center h-full text-gray-500 pt-32">
              Enter a search term to visualize connections
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NetworkPage;
