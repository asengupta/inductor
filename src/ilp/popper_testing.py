from popper.util import Settings, print_prog_score
from popper.loop import learn_solution

settings = Settings(kbpath='input_dir')
prog, score, stats = learn_solution(settings)
if prog != None:
    print_prog_score(prog, score)
