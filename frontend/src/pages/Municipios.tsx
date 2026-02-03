import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MapPin, DollarSign, FileText } from 'lucide-react';
import axios from 'axios';
import MunicipiosMap from '../components/maps/MunicipiosMap';
import DataTable from '../components/ui/DataTable';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Municipio {
  id: number;
  nome: string;
  uf: string;
  latitude: number;
  longitude: number;
  distancia_goiania: number;
  total_licitacoes: number;
  valor_total: number;
}

const Municipios = () => {
  const [distanciaFilter, setDistanciaFilter] = useState<number>(200);

  const { data: municipios, isLoading } = useQuery<Municipio[]>({
    queryKey: ['municipios', distanciaFilter],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/v1/municipios?limit=100`);
      // Mock additional data
      return (response.data.municipios || []).map((m: any) => ({
        ...m,
        latitude: m.latitude || -16.6869 + (Math.random() - 0.5) * 2,
        longitude: m.longitude || -49.2648 + (Math.random() - 0.5) * 2,
        distancia_goiania: m.distancia_goiania || Math.random() * 200,
        total_licitacoes: Math.floor(Math.random() * 100),
        valor_total: Math.random() * 10000000,
      }));
    },
  });

  const filteredMunicipios = municipios?.filter(
    (m) => m.distancia_goiania <= distanciaFilter
  );

  const totalLicitacoes = filteredMunicipios?.reduce((sum, m) => sum + m.total_licitacoes, 0) || 0;
  const valorTotal = filteredMunicipios?.reduce((sum, m) => sum + m.valor_total, 0) || 0;

  const columns = [
    { key: 'nome', header: 'Município' },
    { key: 'uf', header: 'UF' },
    {
      key: 'distancia_goiania',
      header: 'Distância (km)',
      render: (value: number) => value.toFixed(0),
    },
    { key: 'total_licitacoes', header: 'Licitações' },
    {
      key: 'valor_total',
      header: 'Valor Total',
      render: (value: number) => `R$ ${value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Municípios</h1>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Municípios</p>
              <p className="text-3xl font-bold text-gray-900">{filteredMunicipios?.length || 0}</p>
            </div>
            <MapPin className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Licitações</p>
              <p className="text-3xl font-bold text-gray-900">{totalLicitacoes}</p>
            </div>
            <FileText className="w-12 h-12 text-green-500" />
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
            <DollarSign className="w-12 h-12 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Filter */}
      <div className="bg-white shadow rounded-lg p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Distância Máxima de Goiânia: {distanciaFilter} km
        </label>
        <input
          type="range"
          min="50"
          max="200"
          step="10"
          value={distanciaFilter}
          onChange={(e) => setDistanciaFilter(Number(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Map */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Mapa Interativo</h2>
        {isLoading ? (
          <div className="h-96 flex items-center justify-center bg-gray-100 rounded">
            <p>Carregando mapa...</p>
          </div>
        ) : (
          <MunicipiosMap municipios={filteredMunicipios || []} />
        )}
        <div className="mt-4 flex items-center justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span>&lt; R$ 1M</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
            <span>R$ 1M - 10M</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-red-500"></div>
            <span>&gt; R$ 10M</span>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Lista de Municípios</h2>
        {isLoading ? (
          <p>Carregando...</p>
        ) : (
          <DataTable columns={columns} data={filteredMunicipios || []} pageSize={20} />
        )}
      </div>
    </div>
  );
};

export default Municipios;
