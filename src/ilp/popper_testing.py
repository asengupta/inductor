from popper.util import Settings
from popper.loop import learn_solution

settings = Settings(kbpath='ilp3', debug=False, noisy=True)
prog, score, stats = learn_solution(settings)
if prog != None:
    settings.print_prog_score(prog, score)
