import { useMemo } from "react";
import { useLocation, useParams } from "react-router-dom";


export function useProgramInfo() {
    const {programName: programIdAdderss} = useParams()
    const programName = programIdAdderss

    const {search} = useLocation();
    const queryParams = new URLSearchParams(search);
    const programIds = queryParams.getAll("programId")
    
    const programInfo = useMemo(()=>( {programIds, programName}), [programIds, programName])
    return programInfo       
}