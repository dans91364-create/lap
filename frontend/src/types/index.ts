export interface Licitacao {
  id: number;
  numero_compra: string;
  objeto_compra: string;
  modalidade_nome: string;
  valor_total_estimado: number;
  valor_total_homologado?: number;
  data_publicacao_pncp: string;
  data_abertura_proposta?: string;
  municipio_id: number;
  situacao_compra_nome?: string;
}

export interface Anomalia {
  id: number;
  licitacao_id?: number;
  tipo: string;
  descricao?: string;
  valor_detectado?: number;
  valor_referencia?: number;
  percentual_desvio?: number;
  score_risco?: number;
  status: string;
  created_at: string;
}

export interface KPIs {
  total_licitacoes: number;
  licitacoes_abertas: number;
  valor_total_estimado: number;
  valor_total_homologado: number;
  economia_gerada: {
    valor: number;
    percentual: number;
  };
  alertas_pendentes: number;
  anomalias_detectadas: number;
}

export interface ChartData {
  periodo: string;
  total: number;
  valor_total?: number;
}

export interface Municipio {
  id: number;
  municipio: string;
  uf: string;
  codigo_ibge: string;
}

export interface Fornecedor {
  id: number;
  razao_social: string;
  cnpj_cpf: string;
  porte_fornecedor_nome?: string;
}

export interface GovernancaKPIs {
  indice_transparencia: number;
  taxa_sucesso: number;
  tempo_medio_dias: number;
  indice_hhi: number;
  participacao_meepp: number;
  economia_media: number;
}
