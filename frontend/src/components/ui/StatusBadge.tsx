interface StatusBadgeProps {
  status: string;
  type?: 'status' | 'severity' | 'custom';
}

const StatusBadge = ({ status, type = 'status' }: StatusBadgeProps) => {
  const getStatusColor = () => {
    const statusLower = status.toLowerCase();
    
    if (type === 'severity') {
      if (statusLower.includes('crítica') || statusLower === 'alta') return 'bg-red-100 text-red-800';
      if (statusLower === 'média' || statusLower === 'médio') return 'bg-yellow-100 text-yellow-800';
      if (statusLower === 'baixa' || statusLower === 'baixo') return 'bg-green-100 text-green-800';
    }
    
    if (statusLower.includes('ativo') || statusLower.includes('aberto') || statusLower.includes('andamento')) {
      return 'bg-green-100 text-green-800';
    }
    if (statusLower.includes('pendente') || statusLower.includes('aguardando')) {
      return 'bg-yellow-100 text-yellow-800';
    }
    if (statusLower.includes('concluído') || statusLower.includes('finalizado') || statusLower.includes('enviado')) {
      return 'bg-blue-100 text-blue-800';
    }
    if (statusLower.includes('erro') || statusLower.includes('cancelado') || statusLower.includes('impedida')) {
      return 'bg-red-100 text-red-800';
    }
    
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor()}`}>
      {status}
    </span>
  );
};

export default StatusBadge;
