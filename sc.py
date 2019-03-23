import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, ROBOTICSFACILITY, ZEALOT, STALKER, IMMORTAL, COLOSSUS, ROBOTICSBAY
import random


class SentBot(sc2.BotAI):
	def __init__(self):
		self.ITERATIONS_PER_MINUTE = 165
		self.MAX_WORKERS = 70

	async def on_step(self, iteration):
		self.iteration = iteration
		await self.distribute_workers()
		await self.build_workers()
		await self.build_pylons()
		await self.build_offensive_force()
		await self.build_assimilators()
		await self.expand()
		await self.offensive_force_building()
		await self.robotic_bay()
		await self.attack()


	async def build_workers(self):
		if len(self.units(NEXUS))*16 > len(self.units(PROBE)):
			if len(self.units(PROBE)) < self.MAX_WORKERS:
				for nexus in self.units(NEXUS).ready.noqueue:
					if self.can_afford(PROBE):
						await self.do(nexus.train(PROBE))

	async def build_pylons(self):
		if self.supply_left < 2 and not self.already_pending(PYLON):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				if self.can_afford(PYLON):
					await self.build(PYLON, near=nexuses.first)

	async def build_assimilators(self):
		for nexus in self.units(NEXUS).ready:
			vaspenes = self.state.vespene_geyser.closer_than(10.0, nexus)
			for vaspene in vaspenes:
				if not self.can_afford(ASSIMILATOR):
					break
				worker = self.select_build_worker(vaspene.position)
				if worker is None:
					break
				if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
					await self.do(worker.build(ASSIMILATOR, vaspene))

	async def expand(self):
		if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
			await self.expand_now()

	async def offensive_force_building(self):
		if self.units(PYLON).ready.exists:
			pylon = self.units(PYLON).ready.random
			if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
				if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
					await self.build(CYBERNETICSCORE, near = pylon)
			elif len(self.units(GATEWAY)) < 10:
				if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
					await self.build(GATEWAY, near = pylon)
			if self.units(ROBOTICSFACILITY).amount < 2:
				if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
					await self.build(ROBOTICSFACILITY, near = pylon)

	async def robotic_bay(self):
		if self.units(PYLON).ready.exists:
			pylon = self.units(PYLON).ready.random
			if self.units(ROBOTICSBAY).amount < 1:
				if self.can_afford(ROBOTICSBAY) and not self.already_pending(ROBOTICSBAY):
					await self.build(ROBOTICSBAY, near = pylon)

	async def build_offensive_force(self):
		for gateway in self.units(GATEWAY).ready.noqueue:
			if not self.units(STALKER).amount > self.units(COLOSSUS).amount:
				if self.can_afford(STALKER) and self.supply_left > 0:
					await self.do(gateway.train(STALKER))

		for robotics in self.units(ROBOTICSFACILITY).ready.noqueue:
			if self.can_afford(COLOSSUS) and self.supply_left > 0:
				await self.do(robotics.train(COLOSSUS))

	def find_target(self, state):
		if len(self.known_enemy_units) > 0:
			return random.choice(self.known_enemy_units)
		elif len(self.known_enemy_structures) > 0:
			return random.choice(self.known_enemy_structures)
		else:
			return self.enemy_start_locations[0]

	async def attack(self):
		aggressive_units = {STALKER: [15, 5],
							COLOSSUS: [5, 1]}

		for UNIT in aggressive_units:
			if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
				for s in self.units(UNIT).idle:
					await self.do(s.attack(self.find_target(self.state)))

			elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
				if len(self.known_enemy_units) > 0:
					for s in self.units(UNIT).idle:
						await self.do(s.attack(random.choice(self.known_enemy_units)))


		#if self.units(STALKER).amount > 15 and self.units(COLOSSUS).amount < 5:
			#for stalker in self.units(STALKER).idle and self.units(COLOSSUS).idle:
				#await self.do(stalker.attack(self.find_target(self.state)))
		#elif self.units(STALKER).amount > 5:
			#if len(self.known_enemy_units) > 0:
				#for stalker in self.units(STALKER).idle:
					#await self.do(stalker.attack(random.choice(self.known_enemy_units)))

run_game(maps.get("AbyssalReefLE"),[
	Bot(Race.Protoss, SentBot()),
	Computer(Race.Terran, Difficulty.VeryHard)
	], realtime=True)