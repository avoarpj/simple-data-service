**Bem-vindo ao repositório!**

> Este repositório foi arquivado pois o SDS foi incorporado definitivamente ao [Turi](https://github.com/avoarpj/turi); <br>
> Propostas novas ao SDS devem ser feitas diretamente no novo repositório.

# Avoar SDS 📂
O SDS foi feito para gerar datasets nos principais formatos utilizados na web (csv, xml e json) derivados de conjuntos de dados mais complexos, para serem consumidos pelo Avoar e outros sistemas autônomos.

O objetivo com a separação desse, é manter a simplicidade do código principal, que foi feito somente para download dos dados e jogar para dentro do banco, sem nenhuma responsabilidade sobre transformações mais avançadas. Este serviço não serve como proxy ou máscara para as fontes oficiais, e sim oferece conjuntos de dados próprios, que também podem ser consumidos livremente por terceiros.

## Consideções de segurança
O servidor web foi feito para servir os arquivos publicamente, isso significa que não há nenhum tipo de autenticação e nem ratelimit, é recomendado que um proxy reverso esteja na frente para fazer ratelimiting e outras heurísticas de segurança para evitar abusos.

## Self hosting 🚀
Nota: *O Avoar ainda não foi lançado oficalmente. Futuramente, o endereço do SDS será `sds.avoar.net.br`.*

É recomendando que você crie um **venv**, com `python -m venv .venv` e depois ative com base no seu OS.<br>
*Caso vá contribuir, não adicione gerenciadores de pacotes*

**Você precisa saber antes do setup:**
- As pastas `temp-downloads` e `public` podem ser criadas manualmente, mas caso você não crie, os scripts farão isso automaticamente.
- Evite interferir manualmente no arquivo `jobs.sqlite`, ele é exclusivo do *apscheduler* e modificá-lo pode levar a comportamentos inesperados.

### Instruções 📌

1. Instale as dependências: `pip install -r requirements.txt`
2. Navegue para a pasta `src` (obrigatório!): `cd src`
3. Gere uma nova versão dos datasets: `python gen_all.py`<br>
*Tecnicamente você pode não rodar o `gen_all` sem problemas, mas existem cronjobs mensais e provavelmente você não vai querer esperar pela primeira execução*.<br>
*Rode o arquivo com parcimônia, pois você pode acabar fazendo requests em massa e ser bloqueado pelos sistemas do IBGE.*<br><br>
4. Rode o processo do scheduler: `python scheduler.py`
5. Rode o processo do servidor web: `uvicorn server:app`

O passo 5 pode ser substituido por uma configuração em webservers como Nginx/Caddy para servir toda a pasta `public` (pode ser mais vantajoso dependendo do setup).

- Ambos os processos devem ser separados (do contrário, o scheduler bloqueará o servidor web de servir os arquivos).
- *As configurações do servidor como porta e host podem ser feitas diretamente no comando uvicorn*.

