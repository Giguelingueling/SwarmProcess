import numpy as np

#  Represent a creature. That is a Chromosome (input of the function) and a fitness (output of the function)
class Creature(object):
    def __init__(self, id_creature, number_of_dimensions, lower_bound, upper_bound, random, fitness=None,
                 position=None):
        self._random = random

        self._id_creature = id_creature
        self._age = 0

        # Array containing the min and max possible for each position
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        # Get the length of each bound
        bound_distance = []
        for i in range(len(self._lower_bound)):
            bound_distance.append(self._upper_bound[i] - self._lower_bound[i])
        self._bound_distance = np.array(bound_distance)
        self._half_bound_distance = self._bound_distance/2

        self._number_dimensions = number_of_dimensions
        self._velocity = self.generate_vector_random()

        self._max_gaz = 1.0
        self._current_gaz = self._max_gaz


        if position is None:
            self._position = self.generate_vector_random()
        else:
            self._position = position

        if fitness is None:
            # For the fitness, lower is better.
            self._fitness = float('Inf')
        else:
            self._fitness = fitness

        # Add the variable useful for the creature memory
        self._memory_best_position = self._position
        self._memory_best_fitness = self._fitness

        # Add a memory list that keep track of the last 10 positions of the creature.
        self._memory_file = []
        self._allow_curiosity = False


    # Generate the position or the velocity of the creature randomly
    def generate_vector_random(self):
        return self._random.uniform(size=self._number_dimensions) * (self._upper_bound - self._lower_bound) + \
               self._lower_bound

    def calculate_curiosity_direction(self, position_to_get_away_from):
        index_choice = np.random.choice(range(len(position_to_get_away_from)), 10, replace=False)
        subset_position_to_get_away = [position_to_get_away_from[index] for index in index_choice]
        subset_position_to_get_away.append(self._memory_best_position)  # Add the best position found by the creature.
        subset_position_to_get_away.extend(self._memory_file)  # Add the last 3 positions of the creature.

        normalized_subset = subset_position_to_get_away/self._bound_distance
        normalized_position = self._position/self._bound_distance
        gamma = 1/(2*0.1**2)

        difference_between_position_and_points_to_avoid = normalized_subset-normalized_position
        distance_vector_normalized = np.square(np.apply_along_axis(np.linalg.norm, axis=1,
                                                                   arr=difference_between_position_and_points_to_avoid))
        direction = np.dot(difference_between_position_and_points_to_avoid.T,
                           np.exp(distance_vector_normalized*(-1*gamma)))
        # direction *= self._bound_distance
        normalized_direction = direction/np.linalg.norm(direction)
        return normalized_direction


    # BE CAREFUL WITH BEST CREATURE TO SEND A HARD COPY SO THAT IF IT UPDATE THE POSITION IT DOESN'T CHANGE
    # THE BEST CREATURE POSITION
    def update_velocity(self, inertia_factor, self_confidence, swarm_confidence, sense_of_adventure,
                        best_creature_position, allow_curiosity, position_to_get_away_from=None):
        current_motion = inertia_factor*self._velocity
        creature_memory = self_confidence*self._random.rand(self._number_dimensions) * (self._memory_best_position -
                                                                                        self._position)
        swarm_influence = swarm_confidence * self._random.rand(self._number_dimensions) * (best_creature_position
                                                                                           - self._position)
        self._allow_curiosity = allow_curiosity
        if self._allow_curiosity:
            # TODO find the formula to express the creature curiosity
            creature_curiosity_direction = self.calculate_curiosity_direction(position_to_get_away_from)
            random_scalar = self._random.rand()
            creature_curiosity = sense_of_adventure * random_scalar * creature_curiosity_direction * (
                self._bound_distance/2.0) * self._current_gaz
            self._current_gaz *= (1-random_scalar)
            self._velocity = current_motion + creature_memory + creature_curiosity + swarm_influence
        else:
            self._velocity = current_motion + creature_memory + swarm_influence

        # Clamp velocity to half the maximum length in each dimension
        self._velocity = np.where(np.abs(self._velocity) <= self._half_bound_distance, self._velocity,
                                  self._half_bound_distance)

    def update_position(self, best_creature_position):
        new_position = self._position+self._velocity
        # Verify if the new position is out of bound. If it's the case put the creature back in the function research
        # domain by using the reflect method (act as if the boundary are mirrors and the creature photons
        # and put inertia to 0.0 on this dimension. We use this method because it was the one shown to perform the best
        # on average by Helwig et al. (2013)
        for i in range(self._number_dimensions):
            # Make sure we don't go out of bound
            if new_position[i] > self._upper_bound[i]:
                new_position[i] = self._upper_bound[i] - (new_position[i]-self._upper_bound[i])
                self._velocity[i] = 0.0
                # Verify the edge case (extremely unlikely) that the creature goes over the other bound
                # If that's the case. Clamp the creature back to the domain
                if new_position[i] < self._lower_bound[i]:
                    new_position[i] = self._lower_bound[i]
            elif new_position[i] < self._lower_bound[i]:
                new_position[i] = self._lower_bound[i] + (self._lower_bound[i] - new_position[i])
                self._velocity[i] = 0.0
                # Verify the edge case (extremely unlikely) that the creature goes over the other bound
                # If that's the case. Clamp the creature back to the domain
                if new_position[i] > self._upper_bound[i]:
                    new_position[i] = self._upper_bound[i]

        # Before changing the position, store it in the memory file
        if len(self._memory_file) >= 3:  # Make sure we only keep the last 10 positions.
            self._memory_file.pop(0)
        self._memory_file.append(self._position)

        # Finally, update the position.
        self._position = new_position
        if self._allow_curiosity:
            if self._current_gaz <= 0.00001*self._max_gaz:
                if np.all(np.abs(self._position - self._memory_best_position) < 0.01 * self._bound_distance) or np.all(
                   np.abs(best_creature_position - self._memory_best_position) < 0.01 * self._bound_distance):
                    self._max_gaz *= 0.5
                    self._current_gaz = self._max_gaz


    def get_id_creature(self):
        return self._id_creature

    def reset_fitness(self):
        self._fitness = float('Inf')

    def reset_memory(self):
        self._memory_best_position = self._position
        self._memory_best_fitness = self._fitness

    def get_fitness(self):
        return self._fitness

    def get_position(self):
        return self._position

    def set_position(self, position):
        self._position = position

    def set_random_position(self):
        self._position = self.generate_vector_random()

    def set_random_velocity(self):
        self._velocity = self.generate_vector_random()

    def get_best_memory_fitness(self):
        return self._memory_best_fitness

    def get_best_memory_position(self):
        return self._memory_best_position

    def update_fitness(self, fitness_function, best_real_function_value):
        self._fitness, std = fitness_function.get_fitness(self._position, best_real_function_value)
        # If the new fitness is better or equal than its best fitness within memory, update the creature memory
        # The equal is used because on discreet function or with function with plateau, the creature would stop moving
        if self._memory_best_fitness > self._fitness:
            self._memory_best_fitness = self._fitness
            self._memory_best_position = self._position

    def update_creature(self, fitness_function, inertia_factor, self_confidence, swarm_confidence,
                        creature_adventure_sense, current_best_creature_position, best_real_function_value,
                        allow_curiosity=False, position_to_get_away_from=None):
        # Update velocity and position
        self.update_velocity(inertia_factor, self_confidence, swarm_confidence, creature_adventure_sense,
                             current_best_creature_position, allow_curiosity, position_to_get_away_from)
        self.update_position(current_best_creature_position)

        # Calculate the fitness
        self.update_fitness(fitness_function=fitness_function, best_real_function_value=best_real_function_value)

        # The creature is now older
        self._age += 1

    def gaussian_mutation(self):
        # For each value between the index
        for i in range(self._number_dimensions):
            random_sample = self._random.normal()  # Adding a value from a Cauchy distribution
            # Rescale the sample so that the value correspond to 1% of the total range and add it to the gene array.
            new_value = self._position[i] + 0.01 * random_sample * (self._upper_bound[i] - self._lower_bound[i])

            # Make sure we don't go out of bound by making the creature rebound on the edgesd
            if new_value[i] > self._upper_bound[i]:
                new_value[i] = self._upper_bound[i] - (new_value[i] - self._upper_bound[i])
                self._velocity[i] = 0.0
                # Verify the edge case (extremely unlikely) that the creature goes over the other bound
                # If that's the case. Clamp the creature back to the domain
                if new_value[i] < self._lower_bound[i]:
                    new_value[i] = self._lower_bound[i]
            elif new_value[i] < self._lower_bound[i]:
                new_value[i] = self._lower_bound[i] + (self._lower_bound[i] - new_value[i])
                self._velocity[i] = 0.0
                # Verify the edge case (extremely unlikely) that the creature goes over the other bound
                # If that's the case. Clamp the creature back to the domain
                if new_value[i] > self._upper_bound[i]:
                    new_value[i] = self._upper_bound[i]
            self._position[i] = new_value
