import time
import optuna
from ant_colony.aco_tsp_oo import colony

def load_params(file):
    sq_path = 'sqlite:///' + file
    study = optuna.load_study(study_name='optimize_aco', storage=sq_path)
    return study.best_trial.params

def optim_h_params(G, init_node, trials, save=False):
    objective = Objective(G, init_node)
    if save:
        study = optuna.create_study(study_name='optimize_aco',
                                    direction="minimize", 
                                    storage='sqlite:///best_hiper_params.db', 
                                    load_if_exists=True)
        
    else:
        study = optuna.create_study(study_name='optimize_aco', direction="minimize")

    study.optimize(objective, n_trials=trials)

    if save:
        print(f'Hyper-parameters saved in ./best_hiper_params.db')

    return study.best_trial

def sample_params(trial):
    return{
        'n_ants' : trial.suggest_int('n_ants', 2, 2048, log=True),
        'max_iter' : trial.suggest_categorical('max_iter', [1, 10, 100, 200, 300, 400, 500]),
        'rho' : trial.suggest_uniform('rho', 0.0, 1.0),
        'alpha' : trial.suggest_int('alpha', 0, 5),
        'beta' : trial.suggest_int('beta', 1, 5)
    }

class Objective(object):
    def __init__(self, G, init_node):
        self.G = G
        self.init_node = init_node

    def __call__(self, trial):
        aco_params = sample_params(trial)
        colony_ = colony(self.G, self.init_node, **aco_params)
        
        # time algorithm
        start = time.time()
        colony_.solve_tsp()
        end = time.time() 
        # total time in minutes
        total_time = (end - start) / 60
        obj = total_time + (colony_.best_dist)**2
        
        return obj

