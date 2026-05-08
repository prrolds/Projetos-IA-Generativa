import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speech_sdk


# OBJETIVO DESTE SCRIPT:
# 1. Carregar chaves de um arquivo .env.
# 2. Conectar-se ao serviço Azure OpenAI.
# 3. Manter um histórico de conversa (messages_array).
# 4. Enviar um prompt do usuário para a IA.
# 5. Receber uma resposta em FORMATO DE TEXTO.

def falar_texto(texto_para_falar):
    """
    Esta função recebe qualquer string de texto e a transforma em fala.
    """
    global speech_config

    load_dotenv()
    speech_key = os.getenv("API_KEY")
    speech_region = os.getenv("REGION")

    speech_config = speech_sdk.SpeechConfig(speech_key, speech_region)
    speech_config.speech_synthesis_voice_name = "pt-BR-FranciscaNeural"

    if not speech_config:
        print("Erro: A configuração de fala (speech_config) não foi inicializada.")
        return

    print(f"\nSintetizando fala para: '{texto_para_falar}...'")
    
    # Configura a saída de áudio para o alto-falante padrão
    audio_config = speech_sdk.audio.AudioOutputConfig(use_default_speaker=True)
    
    # Cria o "sintetizador"
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config, audio_config)

    # Envia o texto para o Azure e aguarda o áudio
    speak = speech_synthesizer.speak_text_async(texto_para_falar).get()

    # Verifica se a síntese foi bem-sucedida
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Erro na síntese de fala: {speak.reason}")

def main(): 
    try: 
        # 1. CARREGAR VARIÁVEIS DE AMBIENTE
        # O arquivo .env guarda nossas chaves secretas.
       
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        
        # 2. INICIALIZAR O CLIENTE DA IA
        # É assim que nosso código se autentica e conversa com a IA.
        client = AzureOpenAI(
            azure_endpoint=azure_oai_endpoint, 
            api_key=azure_oai_key, 
            api_version="2024-02-15-preview"
        )
        
        # 3. DEFINIR A PERSONALIDADE DA IA (Mensagem do Sistema)
        # É aqui que dizemos à IA como ela deve se comportar.
        system_message = """Eu sou um assistente de IA prestativo.
        Eu respondo perguntas de forma concisa e direta."""
        
        # O 'messages_array' guarda todo o histórico da conversa
        # para que a IA tenha contexto.
        messages_array = [{"role": "system", "content": system_message}]

        print("--- Chatbot IA Iniciado (digite 'quit' para sair) ---")

        while True:
            # 4. OBTER O PROMPT DO USUÁRIO
            input_text = input("Você: ")
            if input_text.lower() == "quit":
                break
            
            # Adicionamos a pergunta do usuário ao histórico
            messages_array.append({"role": "user", "content": input_text})

            # 5. ENVIAR PARA A IA E OBTER RESPOSTA
            print("IA está pensando...")
            response = client.chat.completions.create(
                model=azure_oai_deployment,
                messages=messages_array
            )
            
            # Extraímos o TEXTO da resposta da IA
            generated_text = response.choices[0].message.content

            # Adicionamos a resposta da IA ao histórico
            messages_array.append({"role": "assistant", "content": generated_text})

            # Por enquanto, estamos apenas IMPRIMINDO o texto gerado.
            falar_texto(generated_text)
            
            # PERGUNTA: O que mais poderíamos fazer com a variável 'generated_text'?
            # DESAFIO: Como poderíamos "falar" esse texto em vez de apenas imprimi-lo?

    except Exception as ex:
        print(f"Ocorreu um erro: {ex}")

if __name__ == '__main__': 
    main()