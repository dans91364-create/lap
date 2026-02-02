import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { Award, TrendingUp, Clock, Users } from 'lucide-react';

const Governanca = () => {
  const { data: ranking, isLoading } = useQuery({
    queryKey: ['governanca-ranking'],
    queryFn: async () => {
      const response = await api.get('/api/v1/governanca/ranking');
      return response.data;
    },
  });

  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 70) return 'bg-green-100';
    if (score >= 50) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Governança</h2>
        <p className="mt-1 text-sm text-gray-500">
          Análise de indicadores de governança por município
        </p>
      </div>

      {/* Info Cards */}
      <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Award className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              Sobre os Indicadores
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                O score de governança é calculado com base em múltiplos indicadores:
                transparência (30%), taxa de sucesso (25%), concentração de mercado (20%),
                participação ME/EPP (15%), e economia média (10%).
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Ranking Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            Ranking de Municípios
          </h3>
        </div>
        
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Carregando...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Posição
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Município
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Transparência
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Taxa Sucesso
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ME/EPP
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Economia
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {ranking?.ranking?.map((item: any, index: number) => (
                  <tr key={item.municipio_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {index === 0 && <span className="text-yellow-500">🥇</span>}
                      {index === 1 && <span className="text-gray-400">🥈</span>}
                      {index === 2 && <span className="text-orange-600">🥉</span>}
                      {index > 2 && <span>{index + 1}º</span>}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {item.municipio} - {item.uf}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex items-center">
                        <div className={`${getScoreBg(item.score_governanca)} rounded-full px-3 py-1`}>
                          <span className={`font-semibold ${getScoreColor(item.score_governanca)}`}>
                            {item.score_governanca?.toFixed(1) || 'N/A'}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.indice_transparencia?.toFixed(1) || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.taxa_sucesso?.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.participacao_meepp?.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.economia_media?.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Legenda dos Indicadores
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start">
            <TrendingUp className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-gray-900">Transparência</h4>
              <p className="text-sm text-gray-500">Completude dos dados das licitações (0-100)</p>
            </div>
          </div>
          <div className="flex items-start">
            <Award className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-gray-900">Taxa de Sucesso</h4>
              <p className="text-sm text-gray-500">% de licitações concluídas vs desertadas</p>
            </div>
          </div>
          <div className="flex items-start">
            <Users className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-gray-900">Participação ME/EPP</h4>
              <p className="text-sm text-gray-500">% de vitórias de micro e pequenas empresas</p>
            </div>
          </div>
          <div className="flex items-start">
            <Clock className="h-5 w-5 text-blue-500 mr-2 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-gray-900">Economia Média</h4>
              <p className="text-sm text-gray-500">% médio de economia (estimado vs homologado)</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Governanca;
