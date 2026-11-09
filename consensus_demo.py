import argparse
import asyncio
import json
import random


class Agent(asyncio.DatagramProtocol):
    def __init__(self, agent_id, total, drop_rate, rng):
        self.agent_id, self.total = agent_id, total
        self.drop_rate, self.rng = drop_rate, rng
        self.transport = None
        self.values = {}

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, _addr):
        packet = json.loads(data.decode())
        if packet["round"] >= self.values.get(packet["sender"], (-1, 0))[0]:
            self.values[packet["sender"]] = (packet["round"], packet["value"])

    def broadcast(self, round_no, value, base_port):
        packet = json.dumps({"sender": self.agent_id, "round": round_no, "value": value}).encode()
        for peer in range(self.total):
            if peer != self.agent_id and self.rng.random() >= self.drop_rate:
                self.transport.sendto(packet, ("127.0.0.1", base_port + peer))


async def run(args):
    loop = asyncio.get_running_loop()
    rng = random.Random(args.seed)
    agents, transports = [], []
    for i in range(args.agents):
        agent = Agent(i, args.agents, args.drop_rate, rng)
        transport, _ = await loop.create_datagram_endpoint(
            lambda a=agent: a, local_addr=("127.0.0.1", args.base_port + i)
        )
        agents.append(agent); transports.append(transport)
    estimates = [float(i * 10 + 5) for i in range(args.agents)]
    try:
        for round_no in range(args.rounds):
            for i, agent in enumerate(agents):
                agent.broadcast(round_no, estimates[i], args.base_port)
            await asyncio.sleep(args.interval)
            new = []
            for i, agent in enumerate(agents):
                samples = [estimates[i]] + [v for r, v in agent.values.values() if r >= round_no - 1]
                new.append(sum(samples) / len(samples))
            estimates = new
            disagreement = max(estimates) - min(estimates)
            print(f"round={round_no:02d} disagreement={disagreement:.5f} estimates=" + ",".join(f"{v:.2f}" for v in estimates))
    finally:
        for transport in transports: transport.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--agents", type=int, default=5); p.add_argument("--rounds", type=int, default=40)
    p.add_argument("--interval", type=float, default=0.04); p.add_argument("--drop-rate", type=float, default=0.03)
    p.add_argument("--base-port", type=int, default=17000); p.add_argument("--seed", type=int, default=11)
    asyncio.run(run(p.parse_args()))


if __name__ == "__main__": main()
