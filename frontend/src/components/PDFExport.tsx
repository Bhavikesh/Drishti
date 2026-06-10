import React from 'react';
import { exportAPI } from '../services/api';
import { useAuth } from '../hooks/useAuth';

interface Props {
  chatHistory: any[];
}

const PDFExport: React.FC<Props> = ({ chatHistory }) => {
  const { user } = useAuth();

  const handleExport = async () => {
    if (!user) return;
    try {
      await exportAPI.generatePDF(chatHistory, user.id, user.role);
    } catch (error) {
      console.error('Failed to export PDF', error);
      alert('Failed to generate PDF');
    }
  };

  return (
    <button
      onClick={handleExport}
      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center space-x-2"
    >
      <span>📄 Export PDF</span>
    </button>
  );
};

export default PDFExport;
