import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import type { KPIs, ChartData } from '../types';
import { TrendingUp, TrendingDown, FileText, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const { data: kpis, isLoading: kpisLoading } = useQuery<KPIs>({
    queryKey: ['kpis'],
    queryFn: async () => {
      const response = await api.get('/api/v1/estatisticas/kpis');
      return response.data;
    },
  });

  const { data: porMes } = useQuery<{ series: ChartData[] }>({
    queryKey: ['por-mes'],
    queryFn: async () => {
      const response = await api.get('/api/v1/estatisticas/por-mes');
      return response.data;
    },
  });

  if (kpisLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Carregando...</div>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="mt-1 text-sm text-gray-500">
          Visão geral das licitações públicas
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Licitações */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total de Licitações
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {kpis?.total_licitacoes || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Valor Total */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Valor Total Estimado
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {formatCurrency(kpis?.valor_total_estimado || 0)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Economia */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingDown className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Economia Gerada
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {formatCurrency(kpis?.economia_gerada?.valor || 0)}
                  </dd>
                  <dd className="text-sm text-gray-500">
                    {kpis?.economia_gerada?.percentual.toFixed(2)}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Anomalias */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertCircle className="h-6 w-6 text-red-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Anomalias Detectadas
                  </dt>
                  <dd className="text-2xl font-semibold text-gray-900">
                    {kpis?.anomalias_detectadas || 0}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Licitações por Mês
        </h3>
        <div className="h-64 flex items-center justify-center text-gray-400">
          {porMes?.series && porMes.series.length > 0 ? (
            <div className="w-full">
              <div className="flex justify-between items-end h-48">
                {porMes.series.slice(-12).map((item, index) => (
                  <div key={index} className="flex flex-col items-center flex-1">
                    <div className="w-full mx-1">
                      <div
                        className="bg-blue-500 rounded-t"
                        style={{
                          height: `${(item.total / Math.max(...porMes.series.map(s => s.total))) * 150}px`,
                        }}
                      ></div>
                    </div>
                    <div className="text-xs mt-2 transform -rotate-45 origin-top-left">
                      {item.periodo}
                    </div>
                    <div className="text-xs font-semibold">{item.total}</div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            'Gráfico será exibido quando houver dados'
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
