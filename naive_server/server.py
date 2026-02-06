# This program was modified by VEEVEK AUCKLOO / N01314187

import socket
import argparse
import struct

SEQ_FORMAT = "!I"   
SEQ_SIZE = 4
CHUNK_SIZE = 4096

def run_server(port, output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))

    print(f"[*] Server listening on port {port}")

    try:
        while True:
            f = None
            expected_seq = 0
            buffer = {}          
            eof_seq = None      
            sender_filename = None

            print("==== Start of reception ====")

            while True:
                packet, addr = sock.recvfrom(CHUNK_SIZE + SEQ_SIZE)

                if len(packet) < SEQ_SIZE:
                    continue

                seq = struct.unpack(SEQ_FORMAT, packet[:SEQ_SIZE])[0]
                data = packet[SEQ_SIZE:]

                ack = struct.pack(SEQ_FORMAT, seq)
                sock.sendto(ack, addr)

                # Create output file on first valid packet
                if f is None:
                    ip, sender_port = addr
                    sender_filename = f"received_{ip.replace('.', '_')}_{sender_port}.jpg"
                    f = open(sender_filename, "wb")
                    print(f"[*] Writing to {sender_filename}")

                if len(data) == 0:
                    eof_seq = seq
                else:
                    if seq < expected_seq:
                        continue

                    if seq > expected_seq:
                        if seq not in buffer:
                            buffer[seq] = data
                        continue

                    if seq == expected_seq:
                        f.write(data)
                        expected_seq += 1

                        while expected_seq in buffer:
                            f.write(buffer.pop(expected_seq))
                            expected_seq += 1

                if eof_seq is not None and expected_seq == eof_seq:
                    print(f"[*] Complete (EOF seq={eof_seq}). Closing.")
                    break

            if f:
                f.close()

            print("==== End of reception ====")

    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    finally:
        sock.close()
        print("[*] Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable UDP File Receiver (Reordering + Loss)")
    parser.add_argument("--port", type=int, default=12001, help="Port to listen on")
    parser.add_argument("--output", type=str, default="received_file.jpg", help="(Not used; kept for compatibility)")
    args = parser.parse_args()

    run_server(args.port, args.output)
