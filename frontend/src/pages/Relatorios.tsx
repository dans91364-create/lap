import { useState } from 'react';
import { FileText, Download, Calendar, FileSpreadsheet } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import StatusBadge from '../components/ui/StatusBadge';
import DataTable from '../components/ui/DataTable';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Relatorio {
  id: number;
  tipo: string;
  formato: string;
  filename: string;
  download_url: string;
  status: string;
  created_at: string;
}

const Relatorios = () => {
  const [selectedTipo, setSelectedTipo] = useState('diario');
  const [selectedFormato, setSelectedFormato] = useState('pdf');
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const { data: relatorios, refetch } = useQuery<{ relatorios: Relatorio[] }>({
    queryKey: ['relatorios'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/v1/relatorios/listar`);
      return response.data;
    },
  });

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const payload = {
        tipo: selectedTipo,
        formato: selectedFormato,
        data_inicio: dataInicio || new Date().toISOString().split('T')[0],
        data_fim: dataFim || new Date().toISOString().split('T')[0],
      };

      await axios.post(`${API_URL}/api/v1/relatorios/gerar`, payload);
      refetch();
      alert('Relatório gerado com sucesso!');
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Erro ao gerar relatório');
    } finally {
      setIsGenerating(false);
    }
  };

  const tiposRelatorio = [
    { value: 'diario', label: 'Relatório Diário', icon: Calendar },
    { value: 'licitacoes', label: 'Relatório de Licitações', icon: FileText },
    { value: 'fornecedores', label: 'Ranking de Fornecedores', icon: FileSpreadsheet },
  ];

  const columns = [
    { key: 'tipo', header: 'Tipo' },
    { key: 'formato', header: 'Formato', render: (value: string) => value.toUpperCase() },
    {
      key: 'status',
      header: 'Status',
      render: (value: string) => <StatusBadge status={value} />,
    },
    {
      key: 'created_at',
      header: 'Data',
      render: (value: string) => new Date(value).toLocaleDateString('pt-BR'),
    },
    {
      key: 'download_url',
      header: 'Ações',
      render: (value: string, row: Relatorio) => (
        <a
          href={`${API_URL}${value}`}
          className="inline-flex items-center text-blue-600 hover:text-blue-800"
          download
        >
          <Download className="w-4 h-4 mr-1" />
          Download
        </a>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Relatórios</h1>
      </div>

      {/* Generate Report Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Gerar Novo Relatório</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          {tiposRelatorio.map((tipo) => {
            const Icon = tipo.icon;
            return (
              <button
                key={tipo.value}
                onClick={() => setSelectedTipo(tipo.value)}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  selectedTipo === tipo.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Icon className="w-8 h-8 mb-2 text-blue-600" />
                <h3 className="font-semibold">{tipo.label}</h3>
              </button>
            );
          })}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Formato
            </label>
            <select
              value={selectedFormato}
              onChange={(e) => setSelectedFormato(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
            </select>
          </div>

          {selectedTipo === 'licitacoes' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Início
                </label>
                <input
                  type="date"
                  value={dataInicio}
                  onChange={(e) => setDataInicio(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Fim
                </label>
                <input
                  type="date"
                  value={dataFim}
                  onChange={(e) => setDataFim(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </>
          )}
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {isGenerating ? 'Gerando...' : 'Gerar Relatório'}
        </button>
      </div>

      {/* Recent Reports */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Relatórios Gerados</h2>
        {relatorios?.relatorios && relatorios.relatorios.length > 0 ? (
          <DataTable columns={columns} data={relatorios.relatorios} pageSize={10} />
        ) : (
          <p className="text-gray-500">Nenhum relatório gerado ainda.</p>
        )}
      </div>
    </div>
  );
};

export default Relatorios;
