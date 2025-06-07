member2(_,[]) :- false.
member2(-(K,V), [(-(KX,VX))|_]) :- K==KX,V==VX.
member2(-(K,V), [_|T]) :- member2(-(K,V),T).

get2(_,[],empty).
get2(K, [(-(K,VX))|_],VX) :- !.
get2(K, [_|T],R) :- get2(K,T,R).

put2_(-(K,V),[],Replaced,R) :- Replaced->R=[];R=[-(K,V)].
put2_(-(K,V),[-(K,_)|T],_,[-(K,V)|RX]) :- put2_(-(K,V),T,true,RX).
put2_(-(K,V),[H|T],Replaced,[H|RX]) :- put2_(-(K,V),T,Replaced,RX).

remove2_(_,[],Acc,Acc).
remove2_(K,[-(K,_)|T],Acc,R) :- remove2_(K,T,Acc,R).
remove2_(K,[H|T],Acc,R) :- remove2_(K,T,[H|Acc],R).

put2(-(K,V),Map,R) :- put2_(-(K,V),Map,false,R).
remove2(K,Map,R) :- remove2_(K,Map,[],R).

merge2(Map1,[],Map1).
merge2([],Map2,Map2).
merge2([-(K,V)|T],Map2,R) :- put2(-(K,V),Map2,RX),merge2(T,RX,R).

update_reg(-(reg(ToRegister),reg(FromRegister)),Registers,UpdatedRegisters) :- get2(FromRegister,Registers,Value),
                                                                               update_reg(-(reg(ToRegister),Value),Registers,UpdatedRegisters).
update_reg(-(reg(ToRegister),Value),Registers,UpdatedRegisters) :- put2(-(ToRegister,Value),Registers,UpdatedRegisters).

equate(LHS,LHS,0).
equate(LHS,RHS,1) :- LHS < RHS.
equate(LHS,RHS,-1) :- LHS > RHS.

instruction_pointer_map([],IPMap,_,IPMap).
instruction_pointer_map([Instr|T],IPMap,IPCounter,FinalIPMap) :- put2(-(IPCounter,Instr),IPMap,UpdatedIPMap),
                                                                 UpdatedIPCounter is IPCounter+1,
                                                                 instruction_pointer_map(T,UpdatedIPMap,UpdatedIPCounter,FinalIPMap).


exec_(IP,IPMap,Registers,Flag,TraceAcc,FinalTrace,FinalRegisters,FinalFlag) :- 
                                                    get2(IP,IPMap,Instr),
                                                    exec_helper(IP,IPMap,Instr,Registers,Flag,TraceAcc,FinalTrace,FinalRegisters,FinalFlag).

exec_helper(_,_,empty,Registers,Flag,TraceAcc,TraceAcc,Registers,Flag).
exec_helper(IP,IPMap,Instr,Registers,Flag,TraceAcc,FinalTrace,FinalRegisters,FinalFlag) :-
                                                        writeln("Interpreting " + Instr),
                                                        NextIP is IP+1,
                                                        interpret(Instr,NextIP,Registers,Flag,UpdatedRegisters,UpdatedFlag,UpdatedIP),
%                                                        UpdatedIP is IP+1,
                                                        write("Next IP is " + UpdatedIP),
                                                        exec_(UpdatedIP,IPMap,UpdatedRegisters,UpdatedFlag,TraceAcc,RemainingTrace,FinalRegisters,FinalFlag),
                                                        FinalTrace=[Instr|RemainingTrace],!.

interpret(mvc(reg(ToRegister),Value),NextIP,Registers,Flag,UpdatedRegisters,Flag,NextIP) :- 
                                                        writeln("In mvc" + ToRegister + Registers),
                                                        update_reg(-(reg(ToRegister),Value),Registers,UpdatedRegisters).
interpret(cmp(reg(CmpRegister),CmpValue),NextIP,Registers,_,Registers,UpdatedFlag,NextIP) :- 
                                                        writeln("In cmp" + CmpRegister + Registers),
                                                        get2(CmpRegister,Registers,RegisterValue),
                                                        equate(RegisterValue,CmpValue,UpdatedFlag).

interpret(j(reg(JumpRegister)),NextIP,Registers,Flag,UpdatedRegisters,UpdatedFlag,UpdatedIP) :- 
                                                        writeln("In jmp indirect" + JumpRegister + Registers),
                                                        get2(JumpRegister,Registers,RegisterValue),
                                                        interpret(j(RegisterValue),NextIP,Registers,Flag,UpdatedRegisters,UpdatedFlag,UpdatedIP).

interpret(j(NewIP),_,Registers,Flag,Registers,Flag,NewIP) :- writeln("In jmp direct" + NewIP + Registers).

interpret(jz(reg(JumpRegister)),NextIP,Registers,Flag,UpdatedRegisters,UpdatedFlag,NewIP) :- 
                                                        writeln("In JZ indirect match" + JumpRegister + Registers),
                                                        get2(JumpRegister,Registers,RegisterValue),
                                                        interpret(jz(RegisterValue),NextIP,Registers,Flag,UpdatedRegisters,UpdatedFlag,NewIP).

interpret(jz(NewIP),_,Registers,0,Registers,0,NewIP) :- writeln("In jmpIfZero direct match" + NewIP + Registers).
interpret(jz(_),NextIP,Registers,Flag,Registers,Flag,NextIP) :- Flag\=0.

trace(Program,FinalTrace,FinalRegisters,FinalFlag) :- instruction_pointer_map(Program,[],1,IPMap),
                                                      writeln("IP MAP IS " + IPMap),
                                                      exec_(1,IPMap,[],0,[],FinalTrace,FinalRegisters,FinalFlag).

