# Cucina Italiana — Sistema de Pedidos Online

Sistema web de pedidos para o restaurante **Cucina Italiana**, desenvolvido como trabalho da disciplina de Programação para Web da PUC-Rio.

O sistema permite que clientes naveguem pelo cardápio, montem pedidos e acompanhem o status de entrega. Atendentes gerenciam a fila de pedidos em tempo real, e gerentes administram o cardápio, categorias e usuários do sistema. A autenticação é baseada em perfis com permissões distintas para cada tipo de usuário.

**Integrantes do grupo:**
- Gabriela Soares de Moraes

---

## Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.x | Linguagem principal |
| Django | 6.0.4 | Framework web back-end |
| SQLite | — | Banco de dados (padrão Django) |
| Bootstrap | 5.3.0 (CDN) | Estilização e responsividade |
| Bootstrap Icons | 1.11.3 (CDN) | Ícones da interface |
| python-dotenv | 1.2.2 | Leitura de variáveis de ambiente |
| asgiref | 3.11.1 | Dependência interna do Django |
| sqlparse | 0.5.5 | Dependência interna do Django |
| tzdata | 2026.1 | Suporte a fusos horários |

> **Nota:** O projeto não utiliza JavaScript — toda a interatividade é feita via formulários HTML e lógica server-side em Django.

---

## Escopo do Site

O **Cucina Italiana** é um sistema de gerenciamento de pedidos para restaurante com três perfis de usuário, cada um com acesso restrito às suas funcionalidades.

### Perfis de Usuário e Permissões

| Funcionalidade | Gerente | Atendente | Cliente |
|---|:---:|:---:|:---:|
| Ver cardápio completo (com indisponíveis) | ✅ | ✅ | — |
| Navegar pelo cardápio e montar carrinho | — | — | ✅ |
| Realizar pedido com cartão salvo | — | — | ✅ |
| Acompanhar próprios pedidos | — | — | ✅ |
| Gerenciar cartões salvos | — | — | ✅ |
| Ver fila de pedidos (todos) | — | ✅ | — |
| Atualizar status de pedidos | — | ✅ | — |
| Painel de pedidos (leitura, com filtros) | ✅ | — | — |
| Criar/editar/excluir Categorias | ✅ | — | — |
| Criar/editar/excluir Itens do Cardápio | ✅ | — | — |
| Gerenciar usuários (alterar perfil) | ✅ | — | — |

#### Gerente
Responsável pela administração do sistema. Pode criar, editar e excluir categorias e itens do cardápio (com controle de disponibilidade). Visualiza todos os pedidos no painel com filtros por status e data. Gerencia os perfis de todos os usuários cadastrados, podendo promover ou rebaixar qualquer conta.

#### Atendente
Responsável pela operação da cozinha/balcão. Ao fazer login, é redirecionado diretamente para a **Fila de Pedidos**. Pode filtrar pedidos por status e atualizar o andamento de cada um: *Recebido → Em Preparo → Pronto → Entregue*.

#### Cliente
Acessa o cardápio agrupado por categorias (somente itens disponíveis), seleciona quantidades e monta o carrinho via sessão. Para finalizar o pedido, precisa ter pelo menos um cartão salvo e informar o CVV. Acompanha o histórico e o status de todos os seus pedidos.

---

## Como Rodar Localmente

### Pré-requisitos
- Python 3.10 ou superior instalado
- Git instalado

### Passo a Passo

**1. Clonar o repositório**
```bash
git clone <url-do-repositorio>
cd progWeb
```

**2. Criar e ativar o ambiente virtual**
```bash
# Criar
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/macOS)
source venv/bin/activate
```

**3. Instalar as dependências**
```bash
pip install -r requirements.txt
```

**4. Configurar o arquivo `.env`**

Copie o arquivo de exemplo e preencha com suas credenciais:
```bash
cp .env.exemplo .env
```

Edite o `.env` conforme o ambiente:
```env
# Imprime o link de recuperação de senha no terminal:
EMAIL_BACKEND_TIPO=console

# Gmail (substitua pelas suas credenciais):
EMAIL_BACKEND_TIPO=gmail
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-gmail
```

> O arquivo `.env.exemplo` na raiz do projeto serve como referência com todos os campos necessários.

**5. Rodar as migrations**
```bash
python manage.py migrate
```

**6. Criar superusuário (opcional — para acessar o Django Admin)**
```bash
python manage.py createsuperuser
```

> O superusuário do Django Admin pode ser usado para criar o primeiro usuário **Gerente** do sistema, caso nenhum exista.

**7. Iniciar o servidor**
```bash
python manage.py runserver
```

Acesse em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### Criando o Primeiro Gerente

O auto-cadastro pelo site (`/registro/`) cria sempre um perfil de **Cliente**. Para criar um Gerente:

**Opção A — Via Django Admin:**
1. Acesse [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) com o superusuário
2. Crie um usuário em *Users*
3. Em *Perfils*, altere o tipo para `gerente`

**Opção B — Se já houver um Gerente no sistema:**
1. Faça login como Gerente
2. Acesse **Usuários** no menu
3. Selecione o usuário desejado e altere o perfil para `gerente`

---

### Usuários de Demonstração

Para facilitar os testes, os seguintes usuários de demonstração estão cadastrados no sistema. O gerente tem permissão para gerenciar os demais usuários.

| Perfil | Username | Senha |
|---|---|---|
| Gerente | usergerente | senhager123 |
| Atendente | useratendente | senhaaten123 |
| Cliente | usercliente | senhacli123 |

---

## Manual do Usuário

### Gerente

**Categorias:**
1. Acesse **Categorias** no menu superior
2. Clique em **Nova Categoria** para criar
3. Use os botões **Editar** ou **Excluir** ao lado de cada categoria
   > Atenção: excluir uma categoria remove todos os itens do cardápio vinculados a ela

**Itens do Cardápio:**
1. Acesse **Cardápio** no menu superior
2. Clique em **Novo Item** para cadastrar (nome, descrição, preço, categoria, disponibilidade)
3. Use **Editar** para alterar qualquer campo, incluindo marcar/desmarcar como disponível
4. Use **Excluir** para remover o item definitivamente

**Painel de Pedidos:**
1. Acesse **Painel de Pedidos** no menu
2. Visualize todos os pedidos do restaurante
3. Filtre por status (Recebido, Em Preparo, Pronto, Entregue) e/ou por data
4. O painel é somente leitura — a atualização de status é feita pelo Atendente

**Gerenciar Usuários:**
1. Acesse **Usuários** no menu
2. Veja a lista completa de usuários cadastrados e seus perfis
3. Clique em **Alterar Perfil** ao lado de qualquer usuário para promover/rebaixar entre gerente, atendente e cliente

---

### Atendente

Ao fazer login, o atendente é automaticamente redirecionado para a **Fila de Pedidos**.

**Gerenciar a fila:**
1. Veja todos os pedidos pendentes listados por data/hora
2. Use o filtro de status no topo para focar em uma etapa específica (ex.: somente *Em Preparo*)
3. Em cada pedido, selecione o novo status no menu suspenso e clique em **Atualizar**

**Fluxo de status:**
```
Recebido → Em Preparo → Pronto → Entregue
```

---

### Cliente

**Navegar pelo cardápio e montar o carrinho:**
1. Acesse **Cardápio** no menu
2. Itens estão agrupados por categoria; somente itens disponíveis são exibidos
3. Informe a quantidade desejada de cada item
4. Clique em **Adicionar ao Carrinho**; o carrinho acumula itens de múltiplas adições

**Salvar um cartão:**
1. Acesse **Meus Cartões** no menu
2. Clique em **Adicionar Cartão**
3. Preencha apelido, nome do titular, número do cartão, bandeira, tipo (crédito/débito), validade e CVV
4. O número completo **não é armazenado** — apenas os 4 últimos dígitos ficam salvos

**Realizar um pedido:**
1. Com itens no carrinho, acesse **Pedido** no menu
2. Revise os itens, quantidades e total
3. Adicione uma observação (opcional)
4. Selecione um cartão salvo e insira o CVV correspondente
5. Clique em **Confirmar Pedido**
6. Uma tela de confirmação exibe o resumo e o número do pedido

**Acompanhar pedidos:**
1. Acesse **Meus Pedidos** no menu
2. Veja o histórico completo com os itens, totais e o status atual de cada pedido
3. Atualize a página para ver mudanças de status feitas pelo atendente

**Excluir um cartão salvo:**
1. Acesse **Meus Cartões**
2. Clique em **Excluir** no cartão desejado
3. Confirme na tela seguinte

---

### Recuperação de Senha (todos os perfis)

1. Na tela de login, clique em **Esqueceu sua senha?**
2. Informe o e-mail cadastrado e clique em **Enviar**
3. **Em desenvolvimento** (`EMAIL_BACKEND_TIPO=console` ou `EMAIL_BACKEND_TIPO=gmail`): o link de redefinição aparece no terminal onde o servidor está rodando se EMAIL_BACKEND_TIPO=console e no email informado se EMAIL_BACKEND_TIPO=gmail.
4. **Em produção** (`EMAIL_BACKEND_TIPO=gmail`): o link é enviado para o e-mail informado
5. Acesse o link, defina a nova senha e faça login normalmente

**Alterar senha (estando logado):**
1. Acesse **Meu Perfil** (ícone/nome no menu)
2. Clique em **Alterar Senha**
3. Informe a senha atual e a nova senha duas vezes

---

## O Que Funciona

### Autenticação e Perfis
- [x] Cadastro de novos usuários (sempre cria perfil *Cliente*)
- [x] Login e logout com confirmação
- [x] Redirecionamento pós-login baseado no perfil (atendente vai direto para a fila)
- [x] Controle de acesso por perfil (Gerente, Atendente, Cliente) com redirecionamento automático
- [x] Recuperação de senha por e-mail (console em dev, Gmail SMTP em produção)
- [x] Alteração de senha estando logado
- [x] Edição de dados do próprio perfil (nome e e-mail, com validação de unicidade)

### CRUD — Categorias (Gerente)
- [x] Criar categoria
- [x] Listar categorias
- [x] Editar categoria
- [x] Excluir categoria (com confirmação)

### CRUD — Itens do Cardápio (Gerente)
- [x] Criar item (nome, descrição, preço, categoria, disponibilidade)
- [x] Listar itens com filtro por categoria
- [x] Editar item (todos os campos, incluindo ativar/desativar disponibilidade)
- [x] Excluir item (com confirmação)

### Carrinho e Pedidos (Cliente)
- [x] Montagem do carrinho via sessão (adiciona quantidades por item)
- [x] Revisão do carrinho com subtotais e total calculados
- [x] Campo de observações no pedido
- [x] Finalização do pedido com cartão salvo + validação de CVV
- [x] Tela de confirmação com resumo do pedido
- [x] Histórico de pedidos com itens e status

### Cartões Salvos (Cliente)
- [x] Adicionar cartão (apenas os 4 últimos dígitos do número são armazenados)
- [x] Listar cartões salvos
- [x] Excluir cartão (com confirmação)

### Fila de Pedidos (Atendente)
- [x] Visualizar todos os pedidos por ordem de chegada
- [x] Filtrar por status
- [x] Atualizar status de qualquer pedido

### Painel Gerencial (Gerente)
- [x] Visualizar todos os pedidos com filtros por status e data
- [x] Gerenciar usuários: listar todos e alterar perfil de qualquer um

---

## O Que Não Funciona / Limitações Conhecidas

| Limitação | Descrição |
|---|---|
| **Pagamento simulado** | Não há integração com gateway de pagamento real. O sistema valida apenas o CVV salvo localmente. Todo pedido é automaticamente marcado como *Pago*. |
| **Carrinho baseado em sessão** | O carrinho fica na sessão do Django. Se o servidor for reiniciado em desenvolvimento, o carrinho é perdido. |
| **Exclusão em cascata** | Ao excluir uma **Categoria**, todos os **Itens** vinculados também são permanentemente excluídos. |
| **CVV armazenado** | Para viabilizar a validação no momento do pagamento simulado, o CVV é armazenado no banco de dados. Em um sistema de produção real, isso não seria feito. |
| **Criação do primeiro gerente** | Todo usuário que se registra pelo site entra automaticamente como cliente — isso é uma decisão de segurança intencional. O primeiro usuário com perfil de gerente deve ser criado pelo painel administrativo do Django (`/admin`) ou promovido via terminal. Após existir pelo menos um gerente no sistema, ele pode promover outros usuários diretamente pela página **Gerenciar Usuários** do próprio site. |

---

## Link do Site Publicado

https://cucinaitaliana.pythonanywhere.com/
