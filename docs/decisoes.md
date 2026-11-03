# Decisões e questões abertas

## Disponibilidade

Oferecer para compra somente status `active` com estoque maior que zero.
Itens `discontinued` ou `coming_soon` não se tornam disponíveis por terem estoque.
Busca pode retornar indisponíveis quando explicitamente solicitado, com motivo.

## Preço

Usar apenas promoções com `is_active=1`. Não inferir vigência pelo nome da campanha:
o CSV não tem datas. Havendo mais de uma promoção ativa para o mesmo produto,
recusar carga e exigir revisão; não escolher uma arbitrariamente.
PIX concede 5% sobre tabela somente quando não houver promoção ativa.
Preço promocional inclui tabela, percentual e preço final.
Preços retornados não constituem reserva de estoque ou processamento de compra.

## Manual

- Contatos divergentes: cadastro/capa e seção 7 indicam telefones distintos.
  Não escolher silenciosamente um contato oficial; explicitar divergência e pedir validação.
- Parcelamento: tabela geral e seção 3.1 diferem. Ainda não calcular parcelas.
  Há também ambiguidade na exceção de R$50; solicitar confirmação ao atendimento.
- Frete local de exatamente R$500 não definido: não afirmar gratuidade nem taxa.
- Devolução: falta data de recebimento e canal de compra nos pedidos.
  Previsão de entrega não substitui recebimento efetivo. Consultar informações
  faltantes e encaminhar casos ambíguos; não emitir aprovação automática.
- As respostas sobre políticas devem ser atribuídas ao manual fornecido; este
  protótipo não avalia a validade jurídica das regras do documento.
- Encaminhamento: não dizer que abriu chamado ou encaminhou reclamação sem
  existir integração que confirme a ação.

## Privacidade de pedidos

Dados de clientes não devem ir integralmente ao prompt. A futura ferramenta de
pedidos deve restringir resultados ao cliente associado à sessão. Seleção de
cliente em uma demo será explicitamente uma simulação, não autenticação real.
Número de pedido, nome ou e-mail isoladamente não comprovam identidade.

## Limitações desta versão

Sem LLM, autenticação, interface de chat ou consultas de pedido expostas.
Sem demonstrações conversacionais fabricadas. Busca de políticas lexical com
sinônimos limitados; resultados precisam ser avaliados e podem omitir contexto.
Índice textual gerado do PDF: mudança no PDF exige regeneração do índice.
CSV é snapshot local, sem garantia de atualidade operacional.
