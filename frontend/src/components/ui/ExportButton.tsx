import { Download } from 'lucide-react';

interface ExportButtonProps {
  data: any[];
  filename: string;
  format?: 'csv' | 'json';
  className?: string;
}

const ExportButton = ({ data, filename, format = 'csv', className = '' }: ExportButtonProps) => {
  const exportData = () => {
    let content = '';
    let mimeType = '';
    
    if (format === 'csv') {
      // Convert to CSV
      if (data.length === 0) return;
      
      const headers = Object.keys(data[0]);
      const csvRows = [
        headers.join(','),
        ...data.map(row =>
          headers.map(header => {
            const value = row[header];
            // Escape quotes and wrap in quotes if contains comma
            const escaped = String(value).replace(/"/g, '""');
            return escaped.includes(',') ? `"${escaped}"` : escaped;
          }).join(',')
        )
      ];
      
      content = csvRows.join('\n');
      mimeType = 'text/csv;charset=utf-8;';
    } else {
      // Export as JSON
      content = JSON.stringify(data, null, 2);
      mimeType = 'application/json;charset=utf-8;';
    }
    
    // Create download
    const blob = new Blob([content], { type: mimeType });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${filename}.${format}`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <button
      onClick={exportData}
      className={`inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${className}`}
    >
      <Download className="w-4 h-4 mr-2" />
      Exportar {format.toUpperCase()}
    </button>
  );
};

export default ExportButton;
