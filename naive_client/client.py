# This program was modified by VEEVEK AUCKLOO / N01314187

import socket
import argparse
import os
import struct

SEQ_FORMAT = "!I"
SEQ_SIZE = 4
MAX_PACKET = 4096
CHUNK_SIZE = MAX_PACKET - SEQ_SIZE  
TIMEOUT_SEC = 0.3

def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_SEC)
    server_address = (target_ip, target_port)

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return

    seq = 0

    try:
        with open(input_file, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break

                packet = struct.pack(SEQ_FORMAT, seq) + chunk

                while True:
                    sock.sendto(packet, server_address)
                    try:
                        ack, _ = sock.recvfrom(2048)
                        if len(ack) < SEQ_SIZE:
                            continue
                        ack_num = struct.unpack(SEQ_FORMAT, ack[:SEQ_SIZE])[0]

                        if ack_num >= seq:
                            seq += 1
                            break
                    except socket.timeout:
                        continue

        eof_packet = struct.pack(SEQ_FORMAT, seq)
        while True:
            sock.sendto(eof_packet, server_address)
            try:
                ack, _ = sock.recvfrom(2048)
                if len(ack) < SEQ_SIZE:
                    continue
                ack_num = struct.unpack(SEQ_FORMAT, ack[:SEQ_SIZE])[0]
                if ack_num == seq:
                    break
            except socket.timeout:
                continue

        print("[*] File transfer completed.")

    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stop-and-Wait UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1")
    parser.add_argument("--target_port", type=int, default=12000)
    parser.add_argument("--file", type=str, required=True)
    args = parser.parse_args()
    run_client(args.target_ip, args.target_port, args.file)
