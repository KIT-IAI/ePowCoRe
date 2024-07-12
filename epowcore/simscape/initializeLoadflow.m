function initializeLoadflow(modelName)
%INITIALIZELOADFLOW Calculate the load flow and apply the results to the control blocks.
%   Control Subsystems need to be named after the controlled synchronous machine:
%   For sync. machine "G01" the Subsystem name needs to end with "Control G01".
ldf = power_loadflow(modelName,'solve');

for sm = ldf.sm
    name = get_param(sm.handle,'Name');
    ctrlName = ".*Control " + name;
    ctrlSys = find_system(modelName, 'MatchFilter', @Simulink.match.activeVariants,'regexp','on','Name',ctrlName);
    pref = find_system(ctrlSys, 'MatchFilter', @Simulink.match.activeVariants,'SearchDepth',1,'BlockType','Constant','Name','Pref');
    set_param(pref{1},'Value',num2str(sm.Pmec / sm.Pnom));

    vref = find_system(ctrlSys, 'MatchFilter', @Simulink.match.activeVariants,'SearchDepth',1,'BlockType','Constant','Name','Vref');
    if ~isempty(vref)
        for bus = ldf.bus
            if bus.ID == sm.busID
                set_param(vref{1},'Value',num2str(bus.vref));
                break
            end
        end
    end
    exciterSubsys = find_system(ctrlSys, 'MatchFilter', @Simulink.match.activeVariants,'Name','Exciter');
    % 'ActiveVariants' (default) | 'AllVariants' | 'ActivePlusCodeVariants'
    exciterMask = find_system(exciterSubsys, 'MatchFilter', @Simulink.match.activeVariants,'BlockType','SubSystem');
    if ~isempty(exciterMask)
        set_param(exciterMask{2},'v0',"[" + num2str(abs(sm.Vt)) + " " + num2str(sm.Vf) + "]");
    end
end

end

