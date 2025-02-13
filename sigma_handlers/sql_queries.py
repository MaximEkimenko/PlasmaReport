# ruff: noqa
"""Сырые запросы в sigma nest."""
initial_table = "PartWithQtyInProcess"  # основная таблица справочно
joined_table = "WorkOrderWithPartQuantities"  # присоединённая справочно

work_orders_table = "WO"  # таблица с номерами текущих рабочих подрядов (заказов)
program_table = "Program"  # таблица с названиями программ
full_table = "PIP"  # таблица со всеми данными касательно программ
sigma_users_table = "Users"  # таблица с пользователями sigma


# запрос на получение имён программ(сз) созданных во временном интервале выбираются только программы,
# которые есть в program_table и full_table
programs_name_query = f"""
           SELECT 
                p.ProgramName, p.PostDateTime, p.Material
            FROM 
                dbo.{program_table} p
            WHERE 
                p.PostDateTime > ? -- start_date
                AND p.PostDateTime < ? -- end_date
                AND EXISTS (
                    SELECT 1
                    FROM dbo.{full_table} f
                    WHERE f.ProgramName = p.ProgramName
                )
            GROUP BY 
                p.ProgramName, p.PostDateTime, p.Material
            ORDER BY 
                MAX(p.PostDateTime) DESC
                    """

work_orders_query = f"""
            SELECT
                WONumber,
                CustomerName,
                WODate,
                OrderDate,
                WOData1,
                WOData2,
                DateCreated
            FROM dbo.{work_orders_table}
                WHERE DateCreated > ? --start_date
                    AND DateCreated < ? --end_date
            ORDER BY DateCreated DESC
            """

parts_by_program_query = f"""
            SELECT
                WONumber,
                ProgramName,
                PartName,
                RepeatID,
                QtyInProcess,
                PartLength,
                PartWidth,
                TrueArea,
                RectArea,
                TrueWeight,
                RectWeight,
                CuttingTime,
                CuttingLength,
                PierceQty,
                NestedArea,
                TotalCuttingTime,
                MasterPartQty,
                WOState,
                DueDate,
                RevisionNumber,
                PK_PIP
            FROM dbo.{full_table}
            WHERE ProgramName = ? --program_name
            """

parts_by_wo_query = f"""
            SELECT
                WONumber,
                PartName,
                ProgramName,
                RepeatID,
                QtyInProcess,
                PartLength,
                PartWidth,
                TrueArea,
                RectArea,
                TrueWeight,
                RectWeight,
                CuttingTime,
                CuttingLength,
                PierceQty,
                NestedArea,
                TotalCuttingTime,
                MasterPartQty,
                WOState,
                DueDate,
                RevisionNumber,
                PK_PIP
            FROM dbo.{full_table}
            WHERE WONumber = ? --wo_name
            """


def create_placeholders_params_query(placeholders):
    """Создание текста запроса с подстановкой вопросительных знаков для параметров. """
    return f"""
        SELECT 
            pr.ProgramName,
            
            pr.RepeatID as RepeatIDProgram,
            -- p.RepeatID as RepeatIDPart,
            
            pr.UsedArea,
            
            pr.ScrapFraction,
            pr.MachineName,
            pr.Thickness,
            
            pr.CuttingTime as CuttingTimeProgram,
            p.CuttingTime as CuttingTimePart,
            p.TotalCuttingTime,
            p.CuttingLength,
            
            pr.PostDateTime,
            pr.Material,
            pr.SheetLength,
            pr.SheetWidth,
            pr.ArchivePacketID,
            pr.TimeLineID,
            pr.Comment,
            pr.PostedByUserID,
            pr.UsedArea,
            pr.UsedArea,
            
            us.UserName,
            us.UserFirstName,
            us.UserLastName,
            us.UserEMail,
            us.LastLoginDate,
            
            w.WONumber,
            w.CustomerName,
            w.WODate,
            w.WOData1,
            w.WOData2,
            w.DateCreated,
            w.OrderDate,
            
            p.PartName,
            p.QtyInProcess,
            p.PartLength,
            p.PartWidth,
            p.RectArea,
            p.TrueArea,
            p.TrueWeight,
            p.RectWeight,
            p.NestedArea,
            
            p.PierceQty as PierceQtyPart,
            pr.PierceQty as PierceQtyProgram,
            p.MasterPartQty,
            p.WOState,
            p.DueDate,
            p.RevisionNumber,
            p.PK_PIP       
            
        FROM 
            dbo.{full_table} p
        INNER JOIN 
            dbo.{work_orders_table} w
        ON 
            p.WONumber = w.WONumber
        INNER JOIN 
            dbo.{program_table} pr
        ON 
            p.ProgramName = pr.ProgramName
        INNER JOIN 
            dbo.{sigma_users_table} us
        ON 
            pr.PostedByUserID = us.userid
        WHERE  
            p.ProgramName IN ({placeholders});
        """
