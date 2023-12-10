import json
import ipaddress
import os
import asyncio
from telebot.async_telebot import AsyncTeleBot
import ssl
import requests
import socket
from bs4 import BeautifulSoup
from urllib.parse import urljoin

os.system('clear')

TOKEN = '6890318433:AAFy3GPPOFeMjyyxg_G7sIFGB14niyREe1o'
bot = AsyncTeleBot(TOKEN)

class HostResponse:
    def __init__(self, target, user_agent, proxy, is_multi=False):
        self.target = target
        self.user_agent = user_agent
        self.proxy = proxy
        self.is_multi = is_multi
        self.results = []  # Simpan hasil di dalam memori

    def Subdomain(self):
        try:
            Agents = {'User-Agent': self.user_agent}
            api = f'https://rapiddns.io/subdomain/{self.target}?full=1&down=0'
            r = requests.get(api, headers=Agents).text
            bs = BeautifulSoup(r, 'html.parser')
            tbody = bs.find('tbody')
            if tbody:
                _tr = tbody.find_all('tr')
                rd = set()
                for pilla in _tr:
                    results = pilla.find('td').text
                    lists = results.split()
                    rd.update(lists)
                ls = list(rd)
                for end in ls:
                    self.results.append(end)
        except Exception as e:
            print(f'[!] Error: {e}')

    def Reverseip(self):
        try:
            Agents = {'User-Agent': self.user_agent}
            url = f'https://api.webscan.cc/?action=query&ip={self.target}'
            response = requests.get(url, headers=Agents).json()
            if isinstance(response, list):
                for item in response:
                    domain = item.get('domain', 'Tidak ada domain')
                    self.results.append(domain)
            else:
                print(f"[*] Not found web in ip {self.target}")
        except Exception as e:
            print(f'[!] Error: {e}')

    def Serverheader(self, domain):
        try:
            proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
            if not domain.startswith('https://'):
                domain = "https://" + domain
            req = requests.get(domain, timeout=4, headers={'User-Agent': self.user_agent}, proxies=proxies)
            server = req.headers.get('Server')
            return server
        except:
            pass

    def Statusheader(self, domain):
        try:
            proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
            if not domain.startswith('https://'):
                domain = "https://" + domain
            req = requests.get(domain, timeout=4, headers={'User-Agent': self.user_agent}, proxies=proxies)
            scode = req.status_code
            return scode
        except:
            pass

    def OpenPort(self, domain, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((domain, port))
            return result == 0
        except Exception:
            return False

    def Protocol(self, domain):
        try:
            with socket.create_connection((domain, 443), timeout=4) as sock:
                with ssl.create_default_context().wrap_socket(sock, server_hostname=domain) as sni_socket:
                    protocol_version = sni_socket.version()
                    return protocol_version
        except:
            pass

    def Domainip(self, domain):
        try:
            ip = socket.gethostbyname(domain)
            return ip
        except:
            pass

    async def Result(self):
        Hasil = []
        subdo = await asyncio.to_thread(self.Subdomain)
        reverseip = await asyncio.to_thread(self.Reverseip)

        async def process_domain(data):
            server = await asyncio.to_thread(self.Serverheader, data)
            status = await asyncio.to_thread(self.Statusheader, data)
            protocol = await asyncio.to_thread(self.Protocol, data)
            domainip = await asyncio.to_thread(self.Domainip, data)

            ports_to_try = [80, 443]
            open_ports = []

            for port in ports_to_try:
                if await asyncio.to_thread(self.OpenPort, data, port):
                    open_ports.append(str(port))

            open_ports_str = ','.join(open_ports)
            result = f"■ {data}|{domainip}|{status}|{server}|{open_ports_str}|{protocol}|"
            return result

        tasks = [process_domain(data) for data in self.results]  # Gunakan hasil di dalam memori
        Hasil = await asyncio.gather(*tasks)

        return Hasil

@bot.message_handler(commands=['start'])
async def send_welcome(message):
    msg = "Selamat Datang di Bot Host Checker"
    await bot.reply_to(message, msg)

@bot.message_handler(commands=['how'])
async def send_how(message):
    msg = """
<b>/scan</b>
Untuk scan ip address atau website
<i>Contoh : /scan google.com</i>

<b>Fitur</b>
Beberapa fitur yang baru tersedia di versi ini
<i>Proxy : /scan site.com -p ip:port</i>
    """
    await bot.reply_to(message, msg, parse_mode='HTML')
    
@bot.message_handler(commands=['donasi'])
async def donasi(message):
    msg = """
<b>Donasi</b>
Agar bisa runtime bot ini 24 jam dengan vps/rdp
dan semangat untuk develop bot ini agar lebih baik.

<b>Sociabuzz</b>
https://sociabuzz.com/wannazid
    """
    await bot.reply_to(message, msg, parse_mode='HTML')
    
def is_valid_ip(ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

@bot.message_handler(commands=['scan'])
async def scan_host(message):
    target_list = message.text.split(' ')
    target = target_list[1] if len(target_list) > 1 else None
    if not target:
        await bot.reply_to(message, "Harap berikan setidaknya satu target.")
        return
    elif is_valid_ip(target):
        await bot.reply_to(message, "Pemindaian sedang berlangsung, harap tunggu!")
        proxie_index = message.text.find('-p')
        proxie = message.text[proxie_index + 2:] if proxie_index != -1 else None
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
        proxy = proxie if proxie else None
        host_response = HostResponse(target, user_agent, proxy)
        text_page = await host_response.Result()
        result_message = '\n'.join(text_page)

        max_chunk_length = 4095

        if len(result_message) > max_chunk_length:
            file_path = f'result_{target}.txt'
            with open(file_path, 'w') as file:
                file.write(result_message)
            await bot.send_document(message.chat.id, open(file_path, 'rb'))
            os.remove(file_path)
        else:
            all_result = f"""
            <b>Hasil Pemeriksa Host: {target}</b>

<i>Format: domain|ip|status_code|server|open_port|protocol_v|</i>

{result_message}

            oleh: @respchecker_bot
            pengembang: @malastech
            """
            await bot.reply_to(message, all_result, parse_mode='HTML')

    else:
        await bot.reply_to(message, "Pemindaian sedang berlangsung, harap tunggu!")
        proxie_index = message.text.find('-p')
        proxie = message.text[proxie_index + 2:] if proxie_index != -1 else None
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
        proxy = proxie if proxie else None
        host_response = HostResponse(target, user_agent, proxy)
        text_page = await host_response.Result()
        result_message = '\n'.join(text_page)

        max_chunk_length = 4095

        if len(result_message) > max_chunk_length:
            file_path = f'result_{target}.txt'
            with open(file_path, 'w') as file:
                file.write(result_message)
            await bot.send_document(message.chat.id, open(file_path, 'rb'))
            os.remove(file_path)
        else:
            all_result = f"""
            <b>Hasil Pemeriksa Host: {target}</b>
            
<i>Format: domain|ip|status_code|server|open_port|protocol_v|</i>

{result_message}

            oleh: @respchecker_bot
            pengembang: @malastech
            """
            await bot.reply_to(message, all_result, parse_mode='HTML')

print('[#] Bot sedang berjalan!')
asyncio.run(bot.polling())

