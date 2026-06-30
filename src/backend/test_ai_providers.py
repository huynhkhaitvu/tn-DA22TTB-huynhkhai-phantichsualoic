import requests, json

url = 'http://127.0.0.1:5000/api/suggestions'
code = '''#include <stdio.h>

int main() {
    int a = 1;
    if (a == 2) {
        printf("a is 2\n");
    } else {
        printf("a is not 2\n");
    }
    return 0;
}
'''
providers = ['gemini', 'openrouter', 'groq']

for p in providers:
    print('\n--- PROVIDER:', p, '---')
    try:
        r = requests.post(url, json={'code': code, 'ai_provider': p, 'error_message': ''}, timeout=60)
        print('HTTP', r.status_code)
        try:
            body = r.json()
            print(json.dumps(body, ensure_ascii=False, indent=2)[:4000])
        except Exception:
            print(r.text[:4000])
    except Exception as e:
        print('REQUEST ERROR:', e)

print('\nDone')
