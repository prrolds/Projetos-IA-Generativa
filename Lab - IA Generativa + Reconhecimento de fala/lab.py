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

def ouvir_do_microfone():
    """
    Esta função escuta o microfone e retorna o que foi dito como uma string de texto.
    """
    global speech_config
    
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")

    speech_config = speech_sdk.SpeechConfig(speech_key, speech_region)
    speech_config.speech_recognition_language = "pt-BR"

    if not speech_config:
        print("Erro: A configuração de fala (speech_config) não foi inicializada.")
        return "" # Retorna string vazia em caso de erro

    # Configura o áudio para usar o microfone padrão
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    
    # Cria o "reconhecedor"
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)

    print("Fale agora... (estou ouvindo)")

    # Inicia o reconhecimento. 
    # 'recognize_once_async().get()' espera até que você pare de falar.
    speech = speech_recognizer.recognize_once_async().get()

    # Verifica o resultado
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        # Sucesso! Retorna o texto.
        return speech.text
    elif speech.reason == speech_sdk.ResultReason.NoMatch:
        print("Não consegui entender o que você disse.")
        return "" # Retorna string vazia
    elif speech.reason == speech_sdk.ResultReason.Canceled:
        print("Reconhecimento cancelado.")
        return "" # Retorna string vazia
    else:
        print(f"Erro no reconhecimento: {speech.reason}")
        return "" # Retorna string vazia

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
            # PERGUNTA: O que mais poderíamos fazer com a variável 'input_text'?
            # DESAFIO: Como poderiamos pegar esse texto da voz ao inves dele ser digitado?
            fala = ouvir_do_microfone()
            fala = fala.strip().lower().replace(".","").replace("?","")

            input_text = fala
            if fala == "encerrar":
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
            print("IA: " + generated_text + "\n")
            
           

    except Exception as ex:
        print(f"Ocorreu um erro: {ex}")

if __name__ == '__main__': 
    main()