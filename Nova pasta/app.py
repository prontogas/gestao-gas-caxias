import streamlit as st
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Gestão de Pedidos - Gás e Água",
    page_icon="📦",
    layout="wide"
)

# Simulação de "Banco de Dados" na memória
if 'clientes' not in st.session_state:
    st.session_state['clientes'] = {
        "21999999999": {"nome": "João da Silva", "endereco": "Rua A, 100 - Leme", "limite": 300.0, "devendo": 50.0},
        "21988888888": {"nome": "Maria Oliveira", "endereco": "Av. Nilo Peçanha, 500 - Caxias", "limite": 150.0, "devendo": 0.0}
    }

if 'funcionarios' not in st.session_state:
    st.session_state['funcionarios'] = [
        {"nome": "Carlos Motoboy", "cargo": "Entregador", "telefone": "2197777-7777"},
        {"nome": "Marcos Gás", "cargo": "Entregador / Balcão", "telefone": "2196666-6666"}
    ]

if 'pedidos' not in st.session_state:
    st.session_state['pedidos'] = []

st.title("📦 Sistema de Expedição e Gestão de Depósito")
st.markdown("---")

# Menu Lateral com opções fixas em lista vertical
menu = st.sidebar.radio(
    "Menu Principal", 
    [
        "Novo Pedido", 
        "Central de Pedidos (Expedição)", 
        "Prestação de Contas / Caixa", 
        "🔒 Fechamento de Caixa Geral",
        "📊 Relatório de Vendas do Dia",
        "Cadastrar / Gerenciar Clientes", 
        "Funcionários / Entregadores"
    ]
)

# Botão de facilidade na barra lateral para limpar tudo se precisar durante os testes
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Limpar Todos os Pedidos (Zerar Dia)"):
    st.session_state['pedidos'] = []
    st.sidebar.success("Todos os pedidos foram apagados!")
    st.rerun()

if menu == "Novo Pedido":
    st.subheader("Lançamento de Pedidos (Balcão / Telefone)")
    
    col_tel, col_vazio = st.columns([3, 1])
    with col_tel:
        tel_busca = st.text_input("Telefone do Cliente (Busca Rápida)")
    
    cliente_encontrado = st.session_state['clientes'].get(tel_busca, None)
    
    nome_cliente = ""
    endereco = ""

    if cliente_encontrado:
        disponivel = cliente_encontrado['limite'] - cliente_encontrado['devendo']
        st.success(f"Cliente Encontrado: **{cliente_encontrado['nome']}** | Limite Disponível para Fiado: **R$ {disponivel:.2f}**")
        nome_cliente = cliente_encontrado['nome']
        endereco = cliente_encontrado['endereco']
    else:
        if tel_busca:
            st.warning("Telefone não cadastrado. Preencha os dados abaixo para cadastrar e lançar o pedido:")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            nome_cliente = st.text_input("Nome do Cliente")
        with col_c2:
            endereco = st.text_input("Endereço de Entrega (Rua, Número, Bairro)")

    st.markdown("### 🛒 Itens do Pedido")
    col_prod, col_qtd, col_val = st.columns([2, 1, 1])
    with col_prod:
        produto = st.selectbox(
            "Produto", 
            ["Gás P13 (Reserva)", "Água Mineral 20L", "Água 500ml", "Cerveja / Bebidas"]
        )
    with col_qtd:
        quantidade = st.number_input("Quantidade", min_value=1, value=1)
    with col_val:
        valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.0, value=100.0, format="%.2f")

    total_venda = quantidade * valor_unitario
    st.markdown(f"### **Total da Venda: R$ {total_venda:.2f}**")
    
    forma_pagamento = st.selectbox("Forma de Pagamento Principal", ["Dinheiro", "Pix", "Cartão", "Fiado (Crediário)"])
    observacao = st.text_area("Observação do Pedido (Ex: Troco para R$ 150, portão cinza)")

    if st.button("Lançar Pedido na Fila", type="primary", use_container_width=True):
        if not nome_cliente or not tel_busca or not endereco:
            st.error("Preencha o telefone, o nome e o endereço do cliente!")
        else:
            if not cliente_encontrado:
                st.session_state['clientes'][tel_busca] = {
                    "nome": nome_cliente,
                    "endereco": endereco,
                    "limite": 0.0,
                    "devendo": 0.0
                }
                cliente_encontrado = st.session_state['clientes'][tel_busca]
                st.toast(f"✅ Novo cliente {nome_cliente} salvo na base!", icon="🎉")

            if forma_pagamento == "Fiado (Crediário)":
                disponivel = cliente_encontrado['limite'] - cliente_encontrado['devendo']
                if total_venda > disponivel:
                    st.error(f"❌ Venda fiado negada! Este cliente possui limite disponível de R$ {disponivel:.2f}.")
                    st.stop()
                else:
                    cliente_encontrado['devendo'] += total_venda

            novo_id = len(st.session_state['pedidos']) + 1
            st.session_state['pedidos'].append({
                "id": novo_id,
                "cliente": nome_cliente,
                "telefone": tel_busca,
                "endereco": endereco,
                "produto": produto,
                "quantidade": quantidade,
                "valor": total_venda,
                "pagamento": forma_pagamento,
                "status": "Pendente",
                "entregador": "Nenhum",
                "hora": datetime.now().strftime("%H:%M")
            })
            st.success(f"✅ Pedido #{novo_id} lançado com sucesso e enviado para a Central de Expedição!")

elif menu == "Central de Pedidos (Expedição)":
    st.subheader("🛵 Central de Pedidos Pendentes e Atribuição de Entregadores")
    st.markdown("Atribua o entregador e clique em **Despachar** para enviar para a rua.")

    pedidos_ativos = [p for p in st.session_state['pedidos'] if p['status'] == "Pendente"]

    if not pedidos_ativos:
        st.info("🎉 Nenhum pedido aguardando despacho no momento! A tela está limpa.")
    else:
        lista_nomes_entregadores = [f['nome'] for f in st.session_state['funcionarios']]
        if not lista_nomes_entregadores:
            lista_nomes_entregadores = ["Cadastre um entregador"]

        for p in pedidos_ativos:
            with st.container(border=True):
                col_info1, col_info2, col_Acao = st.columns([2, 2, 2])
                
                with col_info1:
                    st.markdown(f"**Pedido #{p['id']}** — *{p['hora']}*")
                    st.markdown(f"👤 **Cliente:** {p['cliente']} ({p['telefone']})")
                    st.markdown(f"📍 **Endereço:** {p['endereco']}")
                
                with col_info2:
                    st.markdown(f"📦 **Produto:** {p['quantidade']}x {p['produto']}")
                    st.markdown(f"💰 **Valor:** R$ {p['valor']:.2f} ({p['pagamento']})")
                    st.markdown(f"📌 **Status:** `{p['status']}`")
                
                with col_Acao:
                    st.markdown("### Ação")
                    entregador_escolhido = st.selectbox(
                        f"Entregador (Pedido #{p['id']})", 
                        lista_nomes_entregadores, 
                        key=f"ent_{p['id']}"
                    )
                    
                    if st.button("🚀 Despachar para Rua", key=f"btn_env_{p['id']}", use_container_width=True):
                        p['entregador'] = entregador_escolhido
                        p['status'] = "Em Entrega"
                        st.rerun()

elif menu == "Prestação de Contas / Caixa":
    st.subheader("💵 Acerto de Caixa e Ajuste de Formas de Pagamento por Entregador")
    st.markdown("Conferência detalhada por entregador. Caso o cliente mude a forma de pagamento na hora, basta ajustar abaixo.")

    # Inclui pedidos que estão em rota ("Em Entrega") ou que já foram fechados mas precisam de ajuste ("Acertado")
    pedidos_caixa = [p for p in st.session_state['pedidos'] if p['status'] in ["Em Entrega", "Entregue", "Acertado"] and p['entregador'] != "Nenhum"]
    
    if not pedidos_caixa:
        st.info("Nenhum pedido despachado para entregador no momento.")
    else:
        entregadores_com_entregas = list(set([p['entregador'] for p in pedidos_caixa]))
        
        if not entregadores_com_entregas:
            st.info("Nenhum entregador vinculado a pedidos.")
        else:
            selected_entregador = st.selectbox("Selecione o Entregador para Acerto", entregadores_com_entregas)
            
            pedidos_do_cara = [p for p in pedidos_caixa if p['entregador'] == selected_entregador]
            
            st.markdown(f"### Conferência de Pedidos de: **{selected_entregador}**")

            for p in pedidos_do_cara:
                with st.expander(f"Pedido #{p['id']} - {p['cliente']} | Valor: R$ {p['valor']:.2f} | Pagamento Atual: {p['pagamento']} | Status: {p['status']}"):
                    novo_pagamento = st.selectbox(
                        "Forma de Pagamento Realizada", 
                        ["Dinheiro", "Pix", "Cartão", "Fiado (Crediário)"],
                        index=["Dinheiro", "Pix", "Cartão", "Fiado (Crediário)"].index(p['pagamento']) if p['pagamento'] in ["Dinheiro", "Pix", "Cartão", "Fiado (Crediário)"] else 0,
                        key=f"pag_real_{p['id']}"
                    )
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("💾 Salvar Alteração de Pagamento", key=f"salvar_pag_{p['id']}"):
                            p['pagamento'] = novo_pagamento
                            st.success("Forma de pagamento atualizada com sucesso!")
                            st.rerun()
                    with col_b2:
                        if st.button("✅ Marcar como Acertado", key=f"single_acerto_{p['id']}", type="primary"):
                            p['pagamento'] = novo_pagamento
                            p['status'] = "Acertado"
                            st.success(f"Pedido #{p['id']} acertado com sucesso!")
                            st.rerun()

            total_dinheiro = sum([p['valor'] for p in pedidos_do_cara if p['pagamento'] == "Dinheiro"])
            total_pix = sum([p['valor'] for p in pedidos_do_cara if p['pagamento'] == "Pix"])
            total_cartao = sum([p['valor'] for p in pedidos_do_cara if p['pagamento'] == "Cartão"])
            total_fiado = sum([p['valor'] for p in pedidos_do_cara if p['pagamento'] == "Fiado (Crediário)"])

            st.markdown("---")
            st.markdown(f"### 📊 Resumo do Entregador {selected_entregador}:")
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric(label="💵 Dinheiro", value=f"R$ {total_dinheiro:.2f}")
            with col_m2:
                st.metric(label="📱 Pix", value=f"R$ {total_pix:.2f}")
            with col_m3:
                st.metric(label="💳 Cartão", value=f"R$ {total_cartao:.2f}")
            with col_m4:
                st.metric(label="🔴 Fiado", value=f"R$ {total_fiado:.2f}")

            st.markdown("---")
            if st.button(f"🔄 Fechar Caixa deste Entregador", type="primary"):
                for p in pedidos_do_cara:
                    p['status'] = "Acertado"
                st.success(f"Caixa geral de {selected_entregador} fechado com sucesso!")
                st.rerun()

elif menu == "🔒 Fechamento de Caixa Geral":
    st.subheader("🔒 Fechamento de Caixa Geral do Dia")
    st.markdown("Consolidação de todas as formas de pagamento registradas no dia.")

    pedidos_todos = st.session_state['pedidos']

    total_geral_dinheiro = sum([p['valor'] for p in pedidos_todos if p['pagamento'] == "Dinheiro"])
    total_geral_pix = sum([p['valor'] for p in pedidos_todos if p['pagamento'] == "Pix"])
    total_geral_cartao = sum([p['valor'] for p in pedidos_todos if p['pagamento'] == "Cartão"])
    total_geral_fiado = sum([p['valor'] for p in pedidos_todos if p['pagamento'] == "Fiado (Crediário)"])

    faturamento_total_dia = total_geral_dinheiro + total_geral_pix + total_geral_cartao + total_geral_fiado

    st.markdown("### 💰 Totais Acumulados por Forma de Pagamento")
    col_fc1, col_fc2, col_fc3, col_fc4 = st.columns(4)
    with col_fc1:
        st.metric(label="💵 Dinheiro", value=f"R$ {total_geral_dinheiro:.2f}")
    with col_fc2:
        st.metric(label="📱 Pix", value=f"R$ {total_geral_pix:.2f}")
    with col_fc3:
        st.metric(label="💳 Cartão", value=f"R$ {total_geral_cartao:.2f}")
    with col_fc4:
        st.metric(label="🔴 Fiado (Crediário)", value=f"R$ {total_geral_fiado:.2f}")

    st.markdown("---")
    st.info(f"📊 **Faturamento Bruto Geral do Dia:** R$ {faturamento_total_dia:.2f}")

    st.markdown("### 📋 Relação de Todos os Pedidos do Dia")
    if not pedidos_todos:
        st.info("Nenhum pedido lançado ainda. Comece a lançar na aba 'Novo Pedido'!")
    else:
        for p in pedidos_todos:
            with st.container(border=True):
                col_r1, col_r2, col_r3 = st.columns([2, 2, 1])
                with col_r1:
                    st.markdown(f"**Pedido #{p['id']}** — *{p['hora']}*")
                    st.markdown(f"👤 **Cliente:** {p['cliente']}")
                    st.markdown(f"📦 **Item:** {p['quantidade']}x {p['produto']}")
                with col_r2:
                    st.markdown(f"💳 **Pagamento:** `{p['pagamento']}`")
                    st.markdown(f"📌 **Status:** `{p['status']}`")
                    st.markdown(f"🏍️ **Entregador:** {p['entregador']}")
                with col_r3:
                    st.markdown(f"### R$ {p['valor']:.2f}")

elif menu == "📊 Relatório de Vendas do Dia":
    st.subheader("📊 Relatório Consolidado de Vendas (Quantidade e Faturamento por Produto)")
    st.markdown("Acompanhe o volume de produtos vendidos e o faturamento total gerado no dia.")

    pedidos_todos = st.session_state['pedidos']

    if not pedidos_todos:
        st.info("Nenhum pedido registrado no sistema ainda.")
    else:
        resumo_produtos = {}
        for p in pedidos_todos:
            prod = p['produto']
            qtd = p['quantidade']
            val = p['valor']
            
            if prod not in resumo_produtos:
                resumo_produtos[prod] = {"quantidade": 0, "faturamento": 0.0}
            
            resumo_produtos[prod]["quantidade"] += qtd
            resumo_produtos[prod]["faturamento"] += val

        total_geral_faturamento = sum([item["faturamento"] for item in resumo_produtos.values()])
        total_geral_pecas = sum([item["quantidade"] for item in resumo_produtos.values()])

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.metric(label="💰 Faturamento Total do Dia", value=f"R$ {total_geral_faturamento:.2f}")
        with col_g2:
            st.metric(label="📦 Total de Itens Vendidos", value=f"{total_geral_pecas} unidades")

        st.markdown("---")
        st.markdown("### 📋 Detalhamento por Produto")

        for produto, dados in resumo_produtos.items():
            with st.container(border=True):
                col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
                with col_p1:
                    st.markdown(f"#### 🏷️ {produto}")
                with col_p2:
                    st.metric(label="Quantidade Saída", value=f"{dados['quantidade']} un")
                with col_p3:
                    st.metric(label="Total Arrecadado", value=f"R$ {dados['faturamento']:.2f}")

elif menu == "Cadastrar / Gerenciar Clientes":
    st.subheader("👥 Cadastro de Clientes e Liberação de Limite de Crédito")
    
    with st.form("form_cliente"):
        novo_tel = st.text_input("Telefone com DDD (Ex: 219xxxxxxxx) - Chave Única")
        novo_nome = st.text_input("Nome Completo")
        novo_end = st.text_input("Endereço Completo")
        novo_limite = st.number_input("Definir Limite de Crédito Máximo (R$)", min_value=0.0, value=0.0, format="%.2f")
        
        if st.form_submit_button("Salvar / Atualizar Cliente"):
            if novo_tel and novo_nome:
                devendo_atual = 0.0
                if novo_tel in st.session_state['clientes']:
                    devendo_atual = st.session_state['clientes'][novo_tel]['devendo']

                st.session_state['clientes'][novo_tel] = {
                    "nome": novo_nome, 
                    "endereco": novo_end, 
                    "limite": novo_limite, 
                    "devendo": devendo_atual
                }
                st.success(f"Cliente {novo_nome} salvo com sucesso!")
            else:
                st.error("Preencha ao menos o telefone e o nome.")

    st.markdown("### 📋 Clientes Cadastrados na Base")
    for tel, dados in st.session_state['clientes'].items():
        st.info(f"👤 **{dados['nome']}** (Tel: {tel}) \n\n📍 *Endereço:* {dados['endereco']} \n\n💳 *Limite Máximo:* R$ {dados['limite']:.2f} | 🔴 *Devendo Atualmente:* R$ {dados['devendo']:.2f}")

elif menu == "Funcionários / Entregadores":
    st.subheader("🏍️ Cadastro de Entregadores / Funcionários")
    
    with st.form("form_funcionario"):
        func_nome = st.text_input("Nome do Funcionário")
        func_cargo = st.selectbox("Cargo / Função", ["Entregador", "Atendente / Balcão", "Gerente"])
        func_tel = st.text_input("Telefone / Contato")
        
        if st.form_submit_button("Cadastrar Funcionário"):
            if func_nome:
                st.session_state['funcionarios'].append({
                    "nome": func_nome,
                    "cargo": func_cargo,
                    "telefone": func_tel
                })
                st.success(f"Funcionário {func_nome} cadastrado com sucesso!")
            else:
                st.error("Informe o nome do funcionário.")

    st.markdown("### 📋 Equipe Cadastrada")
    for func in st.session_state['funcionarios']:
        st.info(f"**{func['nome']}** — Cargo: {func['cargo']} | Contato: {func['telefone']}")