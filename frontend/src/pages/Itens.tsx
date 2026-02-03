import { useState } from 'react';
import { Search, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import LineChart from '../components/charts/LineChart';
import DataTable from '../components/ui/DataTable';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const Itens = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedItem, setSelectedItem] = useState<string>('');

  const { data: historico } = useQuery({
    queryKey: ['preco-historico', selectedItem],
    queryFn: async () => {
      if (!selectedItem) return null;
      // Mock data - replace with actual API
      const months = [];
      const basePrice = 100 + Math.random() * 200;
      for (let i = 0; i < 24; i++) {
        const date = new Date();
        date.setMonth(date.getMonth() - (23 - i));
        months.push({
          name: date.toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' }),
          value: basePrice + (Math.random() - 0.5) * 50,
        });
      }
      return {
        historico: months,
        stats: {
          media: basePrice,
          mediana: basePrice,
          min: basePrice - 25,
          max: basePrice + 25,
          desvio_padrao: 15,
        },
        tendencia: Math.random() > 0.5 ? 'subindo' : Math.random() > 0.5 ? 'descendo' : 'estável',
      };
    },
    enabled: !!selectedItem,
  });

  const handleSearch = () => {
    if (searchTerm) {
      setSelectedItem(searchTerm);
    }
  };

  const getTrendIcon = (tendencia: string) => {
    if (tendencia === 'subindo') return <TrendingUp className="w-5 h-5 text-red-500" />;
    if (tendencia === 'descendo') return <TrendingDown className="w-5 h-5 text-green-500" />;
    return <Minus className="w-5 h-5 text-gray-500" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Análise de Itens e Preços</h1>
      </div>

      {/* Search */}
      <div className="bg-white shadow rounded-lg p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Buscar Item
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Digite a descrição do item..."
            className="flex-1 border border-gray-300 rounded-md px-4 py-2"
          />
          <button
            onClick={handleSearch}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 inline-flex items-center"
          >
            <Search className="w-4 h-4 mr-2" />
            Buscar
          </button>
        </div>
      </div>

      {selectedItem && historico && (
        <>
          {/* Statistics */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Estatísticas - {selectedItem}</h2>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Tendência:</span>
                {getTrendIcon(historico.tendencia)}
                <span className="font-medium">{historico.tendencia}</span>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm text-gray-600">Média</p>
                <p className="text-xl font-bold">
                  R$ {historico.stats.media.toFixed(2)}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm text-gray-600">Mediana</p>
                <p className="text-xl font-bold">
                  R$ {historico.stats.mediana.toFixed(2)}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm text-gray-600">Mínimo</p>
                <p className="text-xl font-bold text-green-600">
                  R$ {historico.stats.min.toFixed(2)}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm text-gray-600">Máximo</p>
                <p className="text-xl font-bold text-red-600">
                  R$ {historico.stats.max.toFixed(2)}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm text-gray-600">Desvio Padrão</p>
                <p className="text-xl font-bold">
                  R$ {historico.stats.desvio_padrao.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          {/* Price History Chart */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Histórico de Preços (24 meses)</h2>
            <LineChart
              data={historico.historico}
              showAverage={true}
              yAxisLabel="Preço (R$)"
              height={400}
            />
          </div>

          {/* Suppliers */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold mb-4">Fornecedores que Vendem Este Item</h2>
            <DataTable
              columns={[
                { key: 'fornecedor', header: 'Fornecedor' },
                { key: 'municipio', header: 'Município' },
                {
                  key: 'preco',
                  header: 'Último Preço',
                  render: (value: number) => `R$ ${value.toFixed(2)}`,
                },
                { key: 'data', header: 'Data' },
              ]}
              data={[
                {
                  fornecedor: 'Empresa A',
                  municipio: 'Goiânia',
                  preco: historico.stats.media - 10,
                  data: '15/12/2024',
                },
                {
                  fornecedor: 'Fornecedor B',
                  municipio: 'Anápolis',
                  preco: historico.stats.media + 5,
                  data: '10/12/2024',
                },
              ]}
            />
          </div>
        </>
      )}

      {!selectedItem && (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <Search className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600">
            Digite a descrição de um item para visualizar histórico de preços e análises
          </p>
        </div>
      )}
    </div>
  );
};

export default Itens;
