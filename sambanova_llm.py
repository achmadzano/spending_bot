from langchain_sambanova import ChatSambaNovaCloud
from langchain_core.messages import HumanMessage
import re
import os
from dotenv import load_dotenv

load_dotenv()
SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY")

llm = ChatSambaNovaCloud(
    model="Meta-Llama-3.3-70B-Instruct",
    max_tokens=1024,
    temperature=0.7,
    top_p=0.01,
)

def extract_item(text):
    # Ganti satuan 'juta' atau 'juta'/'jt' menjadi 'jt' agar output harga konsisten
    text = text.replace('jt', 'juta').replace('jt', 'Juta').replace('jt', 'JUTA')
    prompt = (
        "Ekstrak nama barang dan harga dari input berikut, lalu outputkan dalam format JSON: "
        '{"nama":..., "harga":...}. '
        'Harga WAJIB berupa string angka dengan titik sebagai pemisah ribuan, tanpa simbol apapun, misal: "30.000". '
        'JANGAN gunakan koma, jangan gunakan Rp, dan JANGAN gunakan integer. '
        f"Input: {text}"
    )
    messages = [
        ("system", "Kamu adalah asisten yang membantu ekstraksi data belanja."),
        ("human", prompt)
    ]
    response = llm.invoke(messages)
    print("=== RAW LLM RESPONSE ===")
    print(response.content)
    match = re.search(r'\{.*\}', response.content)
    if match:
        try:
            import json
            result = json.loads(match.group(0).replace("'", '"'))
            # Post-process harga agar selalu string bertitik ribuan
            harga = result.get("harga", "")
            if isinstance(harga, int):
                harga = f"{harga:,}".replace(",", ".")
            elif isinstance(harga, str):
                # Hilangkan karakter non-digit, lalu format
                angka = ''.join(filter(str.isdigit, harga))
                if angka:
                    harga = f"{int(angka):,}".replace(",", ".")
            result["harga"] = harga
            return result
        except Exception as e:
            print(f"JSON decode error: {e}")
            return None
    print("No JSON found in response.")
    return None

def extract_delete_item(text):
    text = text.replace('jt', 'juta').replace('jt', 'Juta').replace('jt', 'JUTA')
    prompt = (
        "Ekstrak nama barang dan harga dari perintah hapus berikut, lalu outputkan dalam format JSON: "
        '{"nama":..., "harga":...}. '
        'Harga WAJIB berupa string angka dengan titik sebagai pemisah ribuan, tanpa simbol apapun, misal: "30.000". '
        'JANGAN gunakan koma, jangan gunakan Rp, dan JANGAN gunakan integer. '
        f"Input: {text}"
    )
    messages = [
        ("system", "Kamu adalah asisten yang membantu ekstraksi data belanja untuk penghapusan."),
        ("human", prompt)
    ]
    response = llm.invoke(messages)
    import re
    match = re.search(r'\{.*\}', response.content)
    if match:
        try:
            import json
            result = json.loads(match.group(0).replace("'", '"'))
            harga = result.get("harga", "")
            if isinstance(harga, int):
                harga = f"{harga:,}".replace(",", ".")
            elif isinstance(harga, str):
                angka = ''.join(filter(str.isdigit, harga))
                if angka:
                    harga = f"{int(angka):,}".replace(",", ".")
            result["harga"] = harga
            return result
        except Exception as e:
            print(f"JSON decode error: {e}")
            return None
    print("No JSON found in response.")
    return None

def text2num(text):
    # Mapping sederhana kata ke angka
    mapping = {
        'seratus': '100.000',
        'dua ratus': '200.000',
        'tiga ratus': '300.000',
        'empat ratus': '400.000',
        'lima ratus': '500.000',
        'enam ratus': '600.000',
        'tujuh ratus': '700.000',
        'delapan ratus': '800.000',
        'sembilan ratus': '900.000',
        'seribu': '1.000',
        'dua ribu': '2.000',
        'tiga ribu': '3.000',
        'empat ribu': '4.000',
        'lima ribu': '5.000',
        'sepuluh ribu': '10.000',
        'seratus ribu': '100.000',
        'sejuta': '1.000.000',
        'dua juta': '2.000.000',
        'tiga juta': '3.000.000',
        'empat juta': '4.000.000',
        'lima juta': '5.000.000',
        'sepuluh juta': '10.000.000',
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text
