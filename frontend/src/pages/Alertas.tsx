import { useState } from 'react';
import { Plus, Bell, Mail, MessageSquare } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import Modal from '../components/ui/Modal';
import DataTable from '../components/ui/DataTable';
import StatusBadge from '../components/ui/StatusBadge';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Alerta {
  id: number;
  nome: string;
  tipo: string;
  canal: string;
  ativo: boolean;
  created_at: string;
}

const Alertas = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    nome: '',
    tipo: 'licitacao',
    palavras_chave: '',
    valor_minimo: '',
    canal: 'email',
    destinatario: '',
  });

  const { data: alertas, refetch } = useQuery<{ alertas: Alerta[] }>({
    queryKey: ['alertas'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/v1/alertas`);
      return response.data;
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await axios.post(`${API_URL}/api/v1/alertas`, formData);
      setIsModalOpen(false);
      refetch();
      alert('Alerta criado com sucesso!');
      setFormData({
        nome: '',
        tipo: 'licitacao',
        palavras_chave: '',
        valor_minimo: '',
        canal: 'email',
        destinatario: '',
      });
    } catch (error) {
      alert('Erro ao criar alerta');
    }
  };

  const handleToggleAtivo = async (id: number, ativo: boolean) => {
    try {
      await axios.patch(`${API_URL}/api/v1/alertas/${id}`, { ativo: !ativo });
      refetch();
    } catch (error) {
      alert('Erro ao atualizar alerta');
    }
  };

  const getChannelIcon = (canal: string) => {
    if (canal === 'email') return <Mail className="w-4 h-4" />;
    if (canal === 'telegram') return <MessageSquare className="w-4 h-4" />;
    return <Bell className="w-4 h-4" />;
  };

  const columns = [
    { key: 'nome', header: 'Nome' },
    { key: 'tipo', header: 'Tipo' },
    {
      key: 'canal',
      header: 'Canal',
      render: (value: string) => (
        <div className="flex items-center gap-2">
          {getChannelIcon(value)}
          {value}
        </div>
      ),
    },
    {
      key: 'ativo',
      header: 'Status',
      render: (value: boolean) => (
        <StatusBadge status={value ? 'Ativo' : 'Inativo'} />
      ),
    },
    {
      key: 'created_at',
      header: 'Criado em',
      render: (value: string) => new Date(value).toLocaleDateString('pt-BR'),
    },
    {
      key: 'id',
      header: 'Ações',
      render: (value: number, row: Alerta) => (
        <button
          onClick={() => handleToggleAtivo(value, row.ativo)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {row.ativo ? 'Desativar' : 'Ativar'}
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Alertas</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Novo Alerta
        </button>
      </div>

      {/* Alert Types Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <Bell className="w-12 h-12 text-blue-500 mb-3" />
          <h3 className="font-semibold text-lg">Alertas de Licitação</h3>
          <p className="text-sm text-gray-600 mt-2">
            Notificações quando novas licitações são publicadas com base em suas palavras-chave
          </p>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6">
          <Mail className="w-12 h-12 text-green-500 mb-3" />
          <h3 className="font-semibold text-lg">Email</h3>
          <p className="text-sm text-gray-600 mt-2">
            Receba alertas diretamente no seu email
          </p>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6">
          <MessageSquare className="w-12 h-12 text-purple-500 mb-3" />
          <h3 className="font-semibold text-lg">Telegram</h3>
          <p className="text-sm text-gray-600 mt-2">
            Notificações instantâneas via Telegram
          </p>
        </div>
      </div>

      {/* Alerts List */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Meus Alertas</h2>
        {alertas?.alertas && alertas.alertas.length > 0 ? (
          <DataTable columns={columns} data={alertas.alertas} />
        ) : (
          <p className="text-gray-500">Nenhum alerta configurado ainda.</p>
        )}
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Criar Novo Alerta"
        size="md"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nome do Alerta
            </label>
            <input
              type="text"
              value={formData.nome}
              onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo
            </label>
            <select
              value={formData.tipo}
              onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="licitacao">Nova Licitação</option>
              <option value="anomalia">Anomalia Detectada</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Palavras-chave (separadas por vírgula)
            </label>
            <input
              type="text"
              value={formData.palavras_chave}
              onChange={(e) => setFormData({ ...formData, palavras_chave: e.target.value })}
              placeholder="Ex: software, hardware, manutenção"
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Valor Mínimo (R$)
            </label>
            <input
              type="number"
              value={formData.valor_minimo}
              onChange={(e) => setFormData({ ...formData, valor_minimo: e.target.value })}
              placeholder="0.00"
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Canal de Notificação
            </label>
            <select
              value={formData.canal}
              onChange={(e) => setFormData({ ...formData, canal: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="email">Email</option>
              <option value="telegram">Telegram</option>
              <option value="webhook">Webhook</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Destinatário
            </label>
            <input
              type="text"
              value={formData.destinatario}
              onChange={(e) => setFormData({ ...formData, destinatario: e.target.value })}
              placeholder={
                formData.canal === 'email'
                  ? 'email@exemplo.com'
                  : formData.canal === 'telegram'
                  ? 'Chat ID'
                  : 'URL do webhook'
              }
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              required
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Criar Alerta
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Alertas;
