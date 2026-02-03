import { useState } from 'react';
import { Search, AlertTriangle, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface EmpresaImpedida {
  cnpj: string;
  razao_social: string;
  fonte: string;
  uf: string;
  motivo: string;
  data_inicio: string;
}

const CEIS = () => {
  const [searchCNPJ, setSearchCNPJ] = useState('');
  const [fonteFilter, setFonteFilter] = useState<string>('');
  const [ufFilter, setUfFilter] = useState<string>('');
  const [verificacaoResult, setVerificacaoResult] = useState<any>(null);

  const { data: empresas, isLoading, refetch } = useQuery<{ empresas: EmpresaImpedida[] }>({
    queryKey: ['empresas-impedidas', fonteFilter, ufFilter],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (fonteFilter) params.append('fonte', fonteFilter);
      if (ufFilter) params.append('uf', ufFilter);
      
      const response = await axios.get(`${API_URL}/api/v1/ceis-cnep?${params}`);
      return response.data;
    },
  });

  const handleVerificar = async () => {
    if (!searchCNPJ) return;
    
    try {
      const response = await axios.get(`${API_URL}/api/v1/ceis-cnep/verificar/${searchCNPJ}`);
      setVerificacaoResult(response.data);
    } catch (error) {
      setVerificacaoResult({ impedida: false });
    }
  };

  const handleAtualizar = async () => {
    try {
      await axios.post(`${API_URL}/api/v1/ceis-cnep/atualizar`);
      refetch();
      alert('Base atualizada com sucesso!');
    } catch (error) {
      alert('Erro ao atualizar base');
    }
  };

  const columns = [
    {
      key: 'cnpj',
      header: 'CNPJ',
    },
    {
      key: 'razao_social',
      header: 'Razão Social',
    },
    {
      key: 'fonte',
      header: 'Fonte',
      render: (value: string) => <StatusBadge status={value} type="custom" />,
    },
    {
      key: 'uf',
      header: 'UF',
    },
    {
      key: 'motivo',
      header: 'Motivo',
      render: (value: string) => (
        <span className="text-sm">{value?.substring(0, 50)}...</span>
      ),
    },
    {
      key: 'data_inicio',
      header: 'Data',
      render: (value: string) => new Date(value).toLocaleDateString('pt-BR'),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">CEIS/CNEP - Empresas Impedidas</h1>
        <button
          onClick={handleAtualizar}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Atualizar Base
        </button>
      </div>

      {/* Verification */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Verificar CNPJ</h2>
        <div className="flex gap-2">
          <input
            type="text"
            value={searchCNPJ}
            onChange={(e) => setSearchCNPJ(e.target.value)}
            placeholder="Digite o CNPJ..."
            className="flex-1 border border-gray-300 rounded-md px-4 py-2"
          />
          <button
            onClick={handleVerificar}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 inline-flex items-center"
          >
            <Search className="w-4 h-4 mr-2" />
            Verificar
          </button>
        </div>
        
        {verificacaoResult && (
          <div className={`mt-4 p-4 rounded-md ${verificacaoResult.impedida ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
            {verificacaoResult.impedida ? (
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold text-red-900">⚠️ Empresa Impedida!</h3>
                  <p className="text-sm text-red-800 mt-1">
                    Esta empresa consta na base {verificacaoResult.fonte}.
                  </p>
                  {verificacaoResult.motivo && (
                    <p className="text-sm text-red-700 mt-2">
                      <strong>Motivo:</strong> {verificacaoResult.motivo}
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-green-800 font-medium">✓ Empresa não consta como impedida</p>
            )}
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Filtros</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Fonte</label>
            <select
              value={fonteFilter}
              onChange={(e) => setFonteFilter(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Todas</option>
              <option value="CEIS">CEIS</option>
              <option value="CNEP">CNEP</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">UF</label>
            <input
              type="text"
              value={ufFilter}
              onChange={(e) => setUfFilter(e.target.value)}
              placeholder="Ex: GO"
              maxLength={2}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Empresas Impedidas</h2>
        {isLoading ? (
          <p>Carregando...</p>
        ) : (
          <DataTable
            columns={columns}
            data={empresas?.empresas || []}
            pageSize={20}
          />
        )}
      </div>
    </div>
  );
};

export default CEIS;
