import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class StatusSessao(Enum):
    PENDENTE = "pendente"
    REALIZADA = "realizada"


@dataclass
class SessaoEstudo:
    id: int
    materia: str
    topico: str
    duracao_minutos: int
    descricao: str
    status: StatusSessao
    data_criacao: str
    data_realizacao: Optional[str] = None
    
    @property
    def esta_realizada(self) -> bool:
        return self.status == StatusSessao.REALIZADA
    
    def marcar_como_realizada(self) -> None:
        self.status = StatusSessao.REALIZADA
        self.data_realizacao = self._obter_timestamp_atual()
    
    def marcar_como_pendente(self) -> None:
        self.status = StatusSessao.PENDENTE
        self.data_realizacao = None
    
    @staticmethod
    def _obter_timestamp_atual() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def criar_nova(cls, id: int, materia: str, topico: str, 
                   duracao_minutos: int, descricao: str = "") -> 'SessaoEstudo':
        return cls(
            id=id,
            materia=materia,
            topico=topico,
            duracao_minutos=duracao_minutos,
            descricao=descricao,
            status=StatusSessao.PENDENTE,
            data_criacao=cls._obter_timestamp_atual()
        )


class RepositorioSessoes:
    def __init__(self, arquivo: str = "sessoes_estudo.json"):
        self.arquivo = arquivo
    
    def carregar_sessoes(self) -> List[SessaoEstudo]:
        if not os.path.exists(self.arquivo):
            return []
        
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                return [self._dict_para_sessao(item) for item in dados]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def salvar_sessoes(self, sessoes: List[SessaoEstudo]) -> None:
        dados = [self._sessao_para_dict(sessao) for sessao in sessoes]
        with open(self.arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    
    def _dict_para_sessao(self, dados: Dict) -> SessaoEstudo:
        # Compatibilidade com formato antigo
        if 'realizada' in dados:
            status = StatusSessao.REALIZADA if dados['realizada'] else StatusSessao.PENDENTE
        else:
            status = StatusSessao(dados['status'])
        
        return SessaoEstudo(
            id=dados['id'],
            materia=dados['materia'],
            topico=dados['topico'],
            duracao_minutos=dados['duracao_minutos'],
            descricao=dados.get('descricao', ''),
            status=status,
            data_criacao=dados['data_criacao'],
            data_realizacao=dados.get('data_realizacao')
        )
    
    def _sessao_para_dict(self, sessao: SessaoEstudo) -> Dict:
        return {
            'id': sessao.id,
            'materia': sessao.materia,
            'topico': sessao.topico,
            'duracao_minutos': sessao.duracao_minutos,
            'descricao': sessao.descricao,
            'status': sessao.status.value,
            'data_criacao': sessao.data_criacao,
            'data_realizacao': sessao.data_realizacao
        }


class GerenciadorSessoes:
    def __init__(self, repositorio: RepositorioSessoes):
        self._repositorio = repositorio
        self._sessoes = repositorio.carregar_sessoes()
    
    def criar_sessao(self, materia: str, topico: str, 
                    duracao_minutos: int, descricao: str = "") -> SessaoEstudo:
        novo_id = self._obter_proximo_id()
        sessao = SessaoEstudo.criar_nova(novo_id, materia, topico, duracao_minutos, descricao)
        self._sessoes.append(sessao)
        self._salvar()
        return sessao
    
    def marcar_como_realizada(self, id_sessao: int) -> bool:
        sessao = self._buscar_por_id(id_sessao)
        if not sessao:
            return False
        
        if sessao.esta_realizada:
            return False
        
        sessao.marcar_como_realizada()
        self._salvar()
        return True
    
    def marcar_como_pendente(self, id_sessao: int) -> bool:
        sessao = self._buscar_por_id(id_sessao)
        if not sessao:
            return False
        
        if not sessao.esta_realizada:
            return False
        
        sessao.marcar_como_pendente()
        self._salvar()
        return True
    
    def remover_sessao(self, id_sessao: int) -> bool:
        for i, sessao in enumerate(self._sessoes):
            if sessao.id == id_sessao:
                self._sessoes.pop(i)
                self._salvar()
                return True
        return False
    
    def obter_sessoes_pendentes(self) -> List[SessaoEstudo]:
        return [s for s in self._sessoes if not s.esta_realizada]
    
    def obter_sessoes_realizadas(self) -> List[SessaoEstudo]:
        return [s for s in self._sessoes if s.esta_realizada]
    
    def obter_todas_sessoes(self) -> List[SessaoEstudo]:
        return self._sessoes.copy()
    
    def obter_estatisticas(self) -> Dict:
        total = len(self._sessoes)
        realizadas = len(self.obter_sessoes_realizadas())
        pendentes = total - realizadas
        
        tempo_total = sum(s.duracao_minutos for s in self._sessoes)
        tempo_estudado = sum(s.duracao_minutos for s in self.obter_sessoes_realizadas())
        
        return {
            'total': total,
            'realizadas': realizadas,
            'pendentes': pendentes,
            'progresso_percentual': (realizadas / total * 100) if total > 0 else 0,
            'tempo_total_minutos': tempo_total,
            'tempo_estudado_minutos': tempo_estudado
        }
    
    def _obter_proximo_id(self) -> int:
        if not self._sessoes:
            return 1
        return max(s.id for s in self._sessoes) + 1
    
    def _buscar_por_id(self, id_sessao: int) -> Optional[SessaoEstudo]:
        return next((s for s in self._sessoes if s.id == id_sessao), None)
    
    def _salvar(self) -> None:
        self._repositorio.salvar_sessoes(self._sessoes)


class InterfaceUsuario:
    OPCOES_MENU = {
        "1": "Criar nova sessão",
        "2": "Marcar sessão como realizada", 
        "3": "Desmarcar sessão (voltar para pendente)",
        "4": "Listar sessões pendentes",
        "5": "Listar sessões realizadas", 
        "6": "Listar todas as sessões",
        "7": "Ver estatísticas",
        "8": "Remover sessão",
        "0": "Sair"
    }
    
    def __init__(self, gerenciador: GerenciadorSessoes):
        self._gerenciador = gerenciador
    
    def executar(self) -> None:
        while True:
            self._exibir_menu()
            try:
                opcao = input("Escolha uma opção: ").strip()
                
                if opcao == "0":
                    self._exibir_mensagem("👋 Até logo! Bons estudos!")
                    break
                
                self._processar_opcao(opcao)
                self._pausar()
                
            except (ValueError, KeyboardInterrupt):
                self._exibir_erro("Entrada inválida!")
    
    def _exibir_menu(self) -> None:
        print("\n" + "="*50)
        print("📚 SISTEMA DE SESSÕES DE ESTUDO")
        print("="*50)
        for codigo, descricao in self.OPCOES_MENU.items():
            print(f"{codigo}. {descricao}")
        print("-"*50)
    
    def _processar_opcao(self, opcao: str) -> None:
        acoes = {
            "1": self._criar_sessao,
            "2": self._marcar_realizada,
            "3": self._marcar_pendente,
            "4": self._listar_pendentes,
            "5": self._listar_realizadas,
            "6": self._listar_todas,
            "7": self._exibir_estatisticas,
            "8": self._remover_sessao
        }
        
        acao = acoes.get(opcao)
        if acao:
            acao()
        else:
            self._exibir_erro("Opção inválida!")
    
    def _criar_sessao(self) -> None:
        print("\n📝 CRIAR NOVA SESSÃO:")
        materia = input("Matéria: ").strip()
        topico = input("Tópico: ").strip()
        duracao = int(input("Duração (em minutos): "))
        descricao = input("Descrição (opcional): ").strip()
        
        sessao = self._gerenciador.criar_sessao(materia, topico, duracao, descricao)
        self._exibir_sucesso(f"Sessão criada: {sessao.materia} - {sessao.topico}")
    
    def _marcar_realizada(self) -> None:
        self._listar_pendentes()
        if not self._gerenciador.obter_sessoes_pendentes():
            return
        
        id_sessao = int(input("\nID da sessão para marcar como realizada: "))
        if self._gerenciador.marcar_como_realizada(id_sessao):
            self._exibir_sucesso(f"Sessão {id_sessao} marcada como realizada!")
        else:
            self._exibir_erro(f"Não foi possível marcar a sessão {id_sessao}")
    
    def _marcar_pendente(self) -> None:
        self._listar_realizadas()
        if not self._gerenciador.obter_sessoes_realizadas():
            return
        
        id_sessao = int(input("\nID da sessão para desmarcar: "))
        if self._gerenciador.marcar_como_pendente(id_sessao):
            self._exibir_sucesso(f"Sessão {id_sessao} marcada como pendente!")
        else:
            self._exibir_erro(f"Não foi possível desmarcar a sessão {id_sessao}")
    
    def _remover_sessao(self) -> None:
        self._listar_todas()
        if not self._gerenciador.obter_todas_sessoes():
            return
        
        id_sessao = int(input("\nID da sessão para remover: "))
        confirma = input("Tem certeza? (s/N): ").strip().lower()
        
        if confirma == 's' and self._gerenciador.remover_sessao(id_sessao):
            self._exibir_sucesso(f"Sessão {id_sessao} removida!")
        else:
            self._exibir_mensagem("Remoção cancelada.")
    
    def _listar_pendentes(self) -> None:
        sessoes = self._gerenciador.obter_sessoes_pendentes()
        self._exibir_lista_sessoes("📋 SESSÕES PENDENTES", sessoes, "Nenhuma sessão pendente! Parabéns!")
    
    def _listar_realizadas(self) -> None:
        sessoes = self._gerenciador.obter_sessoes_realizadas()
        self._exibir_lista_sessoes("✅ SESSÕES REALIZADAS", sessoes, "Nenhuma sessão realizada ainda!")
    
    def _listar_todas(self) -> None:
        sessoes = self._gerenciador.obter_todas_sessoes()
        self._exibir_lista_sessoes("📚 TODAS AS SESSÕES", sessoes, "Nenhuma sessão cadastrada ainda!")
    
    def _exibir_lista_sessoes(self, titulo: str, sessoes: List[SessaoEstudo], mensagem_vazia: str) -> None:
        if not sessoes:
            self._exibir_mensagem(f"📚 {mensagem_vazia}")
            return
        
        print(f"\n{titulo} ({len(sessoes)}):")
        print("-" * 60)
        
        for sessao in sessoes:
            status_icon = "✅" if sessao.esta_realizada else "⏳"
            status_text = "REALIZADA" if sessao.esta_realizada else "PENDENTE"
            
            print(f"ID: {sessao.id} | {status_icon} {status_text} | {sessao.materia} - {sessao.topico}")
            print(f"   ⏱️  Duração: {sessao.duracao_minutos} min")
            
            if sessao.descricao:
                print(f"   📝 {sessao.descricao}")
            
            print(f"   📅 Criada: {sessao.data_criacao}")
            
            if sessao.esta_realizada and sessao.data_realizacao:
                print(f"   ✅ Realizada: {sessao.data_realizacao}")
            
            print()
    
    def _exibir_estatisticas(self) -> None:
        stats = self._gerenciador.obter_estatisticas()
        
        if stats['total'] == 0:
            self._exibir_mensagem("📊 Nenhuma sessão cadastrada ainda!")
            return
        
        tempo_total_h = stats['tempo_total_minutos'] // 60
        tempo_total_min = stats['tempo_total_minutos'] % 60
        tempo_estudado_h = stats['tempo_estudado_minutos'] // 60
        tempo_estudado_min = stats['tempo_estudado_minutos'] % 60
        
        print(f"\n📊 ESTATÍSTICAS:")
        print("-" * 40)
        print(f"📚 Total de sessões: {stats['total']}")
        print(f"✅ Realizadas: {stats['realizadas']}")
        print(f"⏳ Pendentes: {stats['pendentes']}")
        print(f"📈 Progresso: {stats['progresso_percentual']:.1f}%")
        print(f"⏱️  Tempo total planejado: {stats['tempo_total_minutos']} min ({tempo_total_h}h {tempo_total_min}min)")
        print(f"⏱️  Tempo estudado: {stats['tempo_estudado_minutos']} min ({tempo_estudado_h}h {tempo_estudado_min}min)")
    
    def _exibir_sucesso(self, mensagem: str) -> None:
        print(f"✅ {mensagem}")
    
    def _exibir_erro(self, mensagem: str) -> None:
        print(f"❌ {mensagem}")
    
    def _exibir_mensagem(self, mensagem: str) -> None:
        print(mensagem)
    
    def _pausar(self) -> None:
        input("\nPressione Enter para continuar...")


def main():
    repositorio = RepositorioSessoes()
    gerenciador = GerenciadorSessoes(repositorio)
    interface = InterfaceUsuario(gerenciador)
    interface.executar()


if __name__ == "__main__":
    main()