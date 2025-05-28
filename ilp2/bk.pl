event(loadA).
event(loadB).
event(loadC).
event(loadF).
event(loadG).
event(loadH).

event(advanceA).
event(advanceB).
event(advanceC).
event(advanceF).
event(advanceG).
event(advanceH).

after(loadA, advanceA).
after(loadB, advanceB).
after(loadC, advanceC).
after(advanceF, loadF).
after(advanceH, loadH).
