import struct
import socket
import json
from base64 import b64decode
from codecs import utf_16_be_decode
from colorama import init , Fore
init(autoreset=True)

def ping2MOTD(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.6)
    s.connect((ip, port))
    s.send(bytearray([0xFE, 0x01]))
    data_raw = s.recv(1024)
    s.close()
    return utf_16_be_decode(data_raw[1:])[0].split('\00')[3]

def motd_get_color(motd):
    motd = motd.replace("§0", Fore.LIGHTBLACK_EX)
    motd = motd.replace("§1", Fore.BLUE)
    motd = motd.replace("§2", Fore.GREEN)
    motd = motd.replace("§3", Fore.CYAN)
    motd = motd.replace("§4", Fore.RED)
    motd = motd.replace("§5", Fore.LIGHTRED_EX)
    motd = motd.replace("§6", Fore.YELLOW)
    motd = motd.replace("§7", Fore.LIGHTWHITE_EX)
    motd = motd.replace("§8", Fore.WHITE)
    motd = motd.replace("§9", Fore.LIGHTBLUE_EX)
    motd = motd.replace("§a", Fore.LIGHTGREEN_EX)
    motd = motd.replace("§b", Fore.LIGHTCYAN_EX)
    motd = motd.replace("§c", Fore.LIGHTRED_EX)
    motd = motd.replace("§d", Fore.LIGHTRED_EX)
    motd = motd.replace("§e", Fore.LIGHTYELLOW_EX)
    motd = motd.replace("§f", Fore.WHITE)
    motd = motd.replace("§r", Fore.WHITE)
    motd = motd.replace("§l", "")
    motd = motd.replace("§m", "")
    motd = motd.replace("§n", "")
    motd = motd.replace("§k", "")
    motd = motd.replace("§o", "")
    return motd

def data_processing(ip: str, port: int, data):
    global last_icon, last_server
    if debug:
        print("调试模式:\n" + str(data))
    print('真实地址: ' + socket.gethostbyname(ip) + ":" + str(port))
    print('版本: ' + data['version']['name'] + '  协议编号 ' + str(data['version']['protocol']))
    print('人数: ' + str(data['players']['online']) + '/' + str(data['players']['max']) + "")
    if len(data['players']) > 2:
        num = 0
        for player in data['players']['sample']:
            num += 1
            print("[ " + str(num) + " ] " + motd_get_color(player['name']) + Fore.LIGHTWHITE_EX + " "*int(40 - len(player['name'])) + "UUID: " + player['id'])
    else:
        print("玩家列表: 此服务器没有提供此数据")
    if type(data['description']) == str:
        print("MOTD:")
        print(motd_get_color(data['description']))
    else:
        print(Fore.CYAN + "[ Info ] 获取的 MOTD 信息过于杂乱，为了节省解析时间，使用模式 2 获取")
        print("MOTD:")
        print(motd_get_color(ping2MOTD(ip, port)))
    if 'favicon' in data:
        last_server = ip
        last_icon = data['favicon']
        print(Fore.RED + "[ warn ] 从当前服务器获取到图标，但命令行模式无法显示，可使用 SaveIcon 命令保存")
    if 'modinfo' in data:
        print("MOD 模式: " + data['modinfo']['type'])
        if len(data['modinfo']['modList']) < 1:
            print("MOD 列表: 此服务器没有提供此数据.")
        else:
            print("MOD 列表: " + str(data['modinfo']['modList']))
    else:
        print("MOD 模式: 无 [或服务器没有提供数据]")




# For the rest of requests see wiki.vg/Protocol
def ping(ip: str, port: int):
    def read_var_int():
        i = 0
        j = 0
        while True:
            k = sock.recv(1)
            if not k:
                return 0
            k = k[0]
            i |= (k & 0x7f) << (j * 7)
            j += 1
            if j > 5:
                raise ValueError('var_int too big')
            if not (k & 0x80):
                return i
    #初始化套接字
    sock = socket.socket()
    sock.connect((ip, port))

    try:
        host = ip.encode('utf-8')
        #数据包制作
        data = b''  # wiki.vg/Server_List_Ping
        data += b'\x00'  # packet ID
        data += b'\x04'  # protocol variant
        data += struct.pack('>b', len(host)) + host
        data += struct.pack('>H', port)
        data += b'\x01'  # next state
        data = struct.pack('>b', len(data)) + data
        #发送数据
        sock.sendall(data + b'\x01\x00')  # handshake + status ping

        length = read_var_int()  # full packet length
        if length < 10:
            if length < 0:
                raise ValueError('negative length read')
            else:
                raise ValueError('invalid response %s' % sock.read(length))

        sock.recv(1)  # packet type, 0 for pings
        length = read_var_int()  # string length
        data = b''

        while len(data) != length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                raise ValueError('connection abborted')

            data += chunk
        return json.loads(data)
    finally:
        sock.close()

if __name__ == '__main__':
    last_server = ''
    last_icon = ''
    print("\n" + Fore.LIGHTBLUE_EX + "欢迎使用 MCServerPing For Python")
    print(Fore.YELLOW + "本程序部分源码来自 Github 开发者 Lonami")
    debug = False
    while 1:
        FirstInput = input("\nIP: ").split(':')
        if FirstInput[0] == "SaveIcon":
            if last_server != '' and last_icon != '':
                imgdata = b64decode(last_icon.split(",")[1])
                filename = last_server + '.png'
                with open(filename, 'wb') as f:
                    f.write(imgdata)
                print(Fore.CYAN + "[ Info ] 服务器 " + last_server + " 的图标已保存至程序根目录 " + filename)
            else:
                print(Fore.RED + "[ Error ] 上一个服务器不存在！")
        else:
            if len(FirstInput) < 2:
                FirstInput.append(25565)
            try:
                data_processing(FirstInput[0], int(FirstInput[1]), ping(FirstInput[0], int(FirstInput[1])))
            except Exception as e:
                print("[ Error ] 获取服务器信息时出现错误. 原因" + str(e))