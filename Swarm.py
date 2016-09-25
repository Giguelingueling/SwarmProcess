from Creature import Creature

class Swarm(object):
    def __init__(self, swarm_size, number_of_dimensions, lower_bound, upper_bound, random):
        self._ID = 0
        self._random = random
        self._number_of_dimensions = number_of_dimensions
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._swarm_size = swarm_size
        self._swarm_of_creatures = self.create_creatures(swarm_size)

    def create_creatures(self, swarm_size):
        list_creatures = []
        for i in range(swarm_size):
            list_creatures.append(Creature(self._ID, self._number_of_dimensions, self._lower_bound,
                                           self._upper_bound, self._random))
            self._ID += 1

        return list_creatures

    #Get the creature with the lowest fitness in the swarm.
    def get_best_creature(self):
        best_fitness = float('Inf')
        best_creature = self._swarm_of_creatures[0]
        for creature in self._swarm_of_creatures:
            creature_fitness = creature.get_fitness()
            if creature_fitness < best_fitness:
                best_fitness = creature_fitness
                best_creature = creature
        return best_creature

    def run_swarm_optimization(self, number_of_max_iterations, function_to_optimize):
        for i in range(number_of_max_iterations):
            a=1

    def update_swarm(self, fitness_function, inertia_factor, self_confidence, swarm_confidence,
                     creature_adventure_sense):
        #Before updating, we have to find the best creature of the current swarm iteration.
        best_creature = self._swarm_of_creatures[0]
        best_fitness = best_creature.get_fitness()
        for creature in self._swarm_of_creatures[1::]:
            creature_fitness = creature.get_fitess()
            if(creature.get_fitess() < best_fitness):
                best_creature = creature
                best_fitness = creature_fitness

        #Now that we have the best creature of the current generation, we're ready to call update on all the creatures
        for creature in self._swarm_of_creatures:
            creature.update_creature(fitness_function=fitness_function, inertia_factor=inertia_factor,
                                     self_confidence=self_confidence, swarm_confidence=swarm_confidence,
                                     creature_adventure_sense=creature_adventure_sense,
                                     best_creature_position=best_creature.get_position())