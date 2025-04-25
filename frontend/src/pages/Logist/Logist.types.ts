import { TechProgramType } from "../Techman/Techman.types";

export type LogistProgramType = TechProgramType & {
    RepeatIDProgram: string;
    UsedArea: number;
    ScrapFraction: number;
    MachineName: string;
    CuttingTimeProgram: string;
    Thickness: number;
    SheetLength: number;
    SheetWidth: number;
    ArchivePacketID: number;
    TimeLineID: number;
    Comment: string;
    PostedByUserID: number;
    PierceQtyProgram: number;
    UserFirstName: string;
    UserLastName: string;
    UserEMail: string;
    LastLoginDate: string;
    path_to_ods: string | null;
    master_fio_id: number | null;
    time_program_started: string | null;
    time_program_finished: string | null;
    program_priority: ProgramPriorityType;
    id: number;
    created_at: string;
    updated_at: string;
    wo_numbers: string;
    wo_data1: string;
    program_pic: string;
};
// export type ProgramPriorityType = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export enum ProgramPriorityType {
    LOW = "LOW",
    MEDIUM = "MEDIUM",
    HIGH = "HIGH",
    CRITICAL = "CRITICAL",
}
