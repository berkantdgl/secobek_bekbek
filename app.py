import os
import time
import requests
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login_with_2fa():
    # Web sayfasına gitmek için Selenium'u başlatıyoruz
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    # Web sayfasına git
    driver.get("https://websiteniz.com/login")  # Giriş sayfasının URL'si

    # Kullanıcı adı ve şifre alanlarını bulup doldurma
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys("kullanici_adi")  # Kendi kullanıcı adınızı buraya girin
    password_input.send_keys("sifre")  # Kendi şifrenizi buraya girin

    # Giriş butonuna tıklama
    login_button = driver.find_element(By.NAME, "login")
    login_button.click()

    # "No authentication code?" butonuna tıklama
    time.sleep(2)  # Sayfanın yüklenmesini bekliyoruz
    no_auth_button = driver.find_element(By.LINK_TEXT, "No authentication code?")
    no_auth_button.click()

    # Submit butonuna tıklama
    submit_button = driver.find_element(By.NAME, "submit")
    submit_button.click()

    # 10 saniye bekleme (Power Automate'i tetiklemeden önce)
    time.sleep(10)

    # Power Automate'i tetiklemek için manuel HTTP isteği gönderiyoruz
    automate_url = "https://power-automate-trigger-url.com"  # Power Automate tetikleme URL'niz
    response = requests.post(automate_url)  # Power Automate'i tetikleyen POST isteği
    if response.status_code != 200:
        return jsonify({"error": "Failed to trigger Power Automate"}), 500

    # Power Automate'ten 2FA kodunu almak için 10 saniye bekleme
    time.sleep(10)

    # Power Automate'in geri döneceği URL üzerinden Flask'ın beklemesi gerekiyor
    # Power Automate 'send an http request' ile bu URL'ye geri kod gönderecek
    return jsonify({"status": "Waiting for 2FA code"})


@app.route('/receive_2fa', methods=['POST'])
def receive_2fa():
    # Power Automate'ten gelen POST isteğinde 2FA kodunu alıyoruz
    data = request.get_json()
    two_fa_code = data.get('mailbody')  # Power Automate'in gönderdiği kod

    # Login code alanına bu kodu yapıştırma
    driver = webdriver.Chrome(options=webdriver.ChromeOptions().add_argument("--headless"))
    driver.get("https://websiteniz.com/login")  # Sayfayı tekrar açmak gerekebilir (ya da aynı driver'ı koruyabilirsiniz)
    
    login_code_input = driver.find_element(By.NAME, "login_code")
    login_code_input.send_keys(two_fa_code)

    # Log in butonuna basma
    login_button = driver.find_element(By.NAME, "login_button")
    login_button.click()

    # Sayfanın tam yüklenmesini bekle (örneğin, 5 saniye)
    time.sleep(5)

    # Sayfadan gerekli bilgiyi çekme (örneğin, availability alanı)
    availability = driver.find_element(By.CLASS_NAME, "availability").text

    # Çekilen veriyi JSON formatında döndürme
    driver.quit()  # Tarayıcıyı kapatma
    return jsonify({
        "status": "Login successful",
        "availability": availability
    })


if __name__ == '__main__':
    # Render.com tarafından sağlanan portu kullanma
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
