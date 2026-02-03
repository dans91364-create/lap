import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Building2, TrendingUp, DollarSign, Award, AlertTriangle } from 'lucide-react';
import axios from 'axios';
import PieChart from '../components/charts/PieChart';
import BarChart from '../components/charts/BarChart';
import DataTable from '../components/ui/DataTable';
import ExportButton from '../components/ui/ExportButton';
import { Link } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Fornecedor {
  id: number;
  razao_social: string;
  cnpj: string;
  porte: string;
  total_vitorias: number;
  valor_total_ganho: number;
  impedida: boolean;
}

const Fornecedores = () => {
  const [porteFilter, setPorteFilter] = useState<string>('');
  const [ufFilter, setUfFilter] = useState<string>('');

  const { data: fornecedores, isLoading } = useQuery<Fornecedor[]>({
    queryKey: ['fornecedores'],
    queryFn: async () => {
      // Mock data - replace with actual API call
      return [
        {
          id: 1,
          razao_social: 'Empresa A LTDA',
          cnpj: '12.345.678/0001-90',
          porte: 'ME',
          total_vitorias: 15,
          valor_total_ganho: 450000,
          impedida: false,
        },
        {
          id: 2,
          razao_social: 'Fornecedor B SA',
          cnpj: '98.765.432/0001-10',
          porte: 'EPP',
          total_vitorias: 22,
          valor_total_ganho: 1250000,
          impedida: false,
        },
        {
          id: 3,
          razao_social: 'Grande Corp',
          cnpj: '11.222.333/0001-44',
          porte: 'Demais',
          total_vitorias: 35,
          valor_total_ganho: 5500000,
          impedida: false,
        },
      ];
    },
  });

  const filteredFornecedores = fornecedores?.filter((f) => {
    if (porteFilter && f.porte !== porteFilter) return false;
    return true;
  });

  // Statistics
  const totalFornecedores = filteredFornecedores?.length || 0;
  const valorTotal = filteredFornecedores?.reduce((sum, f) => sum + f.valor_total_ganho, 0) || 0;
  const meEppCount = filteredFornecedores?.filter((f) => ['ME', 'EPP'].includes(f.porte)).length || 0;
  const meEppPercentage = totalFornecedores > 0 ? (meEppCount / totalFornecedores) * 100 : 0;

  // Chart data
  const porteData = [
    {
      name: 'ME',
      value: filteredFornecedores?.filter((f) => f.porte === 'ME').length || 0,
    },
    {
      name: 'EPP',
      value: filteredFornecedores?.filter((f) => f.porte === 'EPP').length || 0,
    },
    {
      name: 'Demais',
      value: filteredFornecedores?.filter((f) => f.porte === 'Demais').length || 0,
    },
  ];

  const topFornecedores =
    filteredFornecedores
      ?.sort((a, b) => b.valor_total_ganho - a.valor_total_ganho)
      .slice(0, 10)
      .map((f) => ({
        name: f.razao_social.substring(0, 20),
        value: f.valor_total_ganho,
      })) || [];

  const columns = [
    {
      key: 'razao_social',
      header: 'Razão Social',
      render: (value: string, row: Fornecedor) => (
        <div className="flex items-center">
          <Link to={`/fornecedores/${row.id}`} className="text-blue-600 hover:text-blue-800">
            {value}
          </Link>
          {row.impedida && (
            <AlertTriangle className="w-4 h-4 text-red-500 ml-2" title="Empresa Impedida" />
          )}
        </div>
      ),
    },
    { key: 'cnpj', header: 'CNPJ' },
    { key: 'porte', header: 'Porte' },
    {
      key: 'total_vitorias',
      header: 'Vitórias',
      render: (value: number) => (
        <span className="inline-flex items-center">
          <Award className="w-4 h-4 mr-1 text-yellow-500" />
          {value}
        </span>
      ),
    },
    {
      key: 'valor_total_ganho',
      header: 'Valor Total',
      render: (value: number) => `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Fornecedores</h1>
        <ExportButton data={filteredFornecedores || []} filename="fornecedores" format="csv" />
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Fornecedores</p>
              <p className="text-3xl font-bold text-gray-900">{totalFornecedores}</p>
            </div>
            <Building2 className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Valor Total</p>
              <p className="text-3xl font-bold text-gray-900">
                R$ {(valorTotal / 1000000).toFixed(1)}M
              </p>
            </div>
            <DollarSign className="w-12 h-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">ME/EPP %</p>
              <p className="text-3xl font-bold text-gray-900">{meEppPercentage.toFixed(1)}%</p>
            </div>
            <TrendingUp className="w-12 h-12 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Filtros</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Porte</label>
            <select
              value={porteFilter}
              onChange={(e) => setPorteFilter(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Todos</option>
              <option value="ME">ME</option>
              <option value="EPP">EPP</option>
              <option value="Demais">Demais</option>
            </select>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Distribuição por Porte</h2>
          <PieChart data={porteData} />
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Top 10 Fornecedores por Valor</h2>
          <BarChart data={topFornecedores} color="#10b981" />
        </div>
      </div>

      {/* Table */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Ranking de Fornecedores</h2>
        {isLoading ? (
          <p>Carregando...</p>
        ) : (
          <DataTable columns={columns} data={filteredFornecedores || []} pageSize={20} />
        )}
      </div>
    </div>
  );
};

export default Fornecedores;
