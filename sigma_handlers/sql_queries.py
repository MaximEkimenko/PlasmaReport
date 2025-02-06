# ruff: noqa
"""Сырые запросы в sigma nest."""
initial_table = "PartWithQtyInProcess"  # основная таблица справочно
joined_table = "WorkOrderWithPartQuantities"  # присоединённая справочно

work_orders_table = "WO"  # таблица с номерами текущих рабочих подрядов (заказов)
program_table = "Program"  # таблица с названиями программ
full_table = "PIP"  # таблица со всеми данными касательно программ
sigma_users_table = "Users"  # таблица с пользователями sigma


# запрос на получение данных программ(сз) по всем программам во временном интервале
programs_name_query = f"""
            SELECT
            ProgramName,
            RepeatID,           
            UsedArea,
            ScrapFraction,
            MachineName,
            CuttingTime,
            PierceQty,
            PostDateTime,
            Material,
            Thickness,
            SheetLength,
            SheetWidth,
            ArchivePacketID,
            TimeLineID,
            Comment,
            PostedByUserID,
            dbo.{sigma_users_table}.UserName,
            dbo.{sigma_users_table}.UserFirstName,
            dbo.{sigma_users_table}.UserLastName,
            dbo.{sigma_users_table}.UserEMail,
            dbo.{sigma_users_table}.LastLoginDate
            FROM dbo.{program_table}
            INNER JOIN dbo.{sigma_users_table}
            ON dbo.{program_table}.PostedByUserID=dbo.{sigma_users_table}.userid
            WHERE PostDateTime > ? --start_date
            AND PostDateTime < ? --end_date
            ORDER BY PostDateTime DESC
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
            PK_PIP,
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





# TODO DEPRECATED
# запрос на данные в интервале
main_query = """
            SELECT
            PartName,
            OrderDate,
            DateCreated,
            Cuttingtime,
            Material,
            Thickness,
            NetArea,
            Netweight,
            RectArea,
            RectWeight,
            QtyRemaining,
            WODate,
            dbo.PartWithQtyInProcess.QtyCompleted,
            dbo.PartWithQtyInProcess.QtyInProcess,
            dbo.PartWithQtyInProcess.QtyOrdered,
            dbo.PartWithQtyInProcess.WONumber
            FROM dbo.WorkOrderWithPartQuantities
            INNER JOIN dbo.PartWithQtyInProcess
            ON dbo.PartWithQtyInProcess.WONumber=dbo.WorkOrderWithPartQuantities.WONumber
            WHERE OrderDate > ? --start_date
            AND OrderDate < ? --end_date
            ORDER BY DateCreated
            """

# запрос на получение списка колонок
column_query = """
            SELECT
            PartName,
            OrderDate,
            DateCreated,
            Cuttingtime,
            Material,
            Thickness,
            NetArea,
            Netweight,
            RectArea,
            RectWeight,
            QtyRemaining,
            WODate,
            dbo.WorkOrderWithPartQuantities.QtyCompleted,
            dbo.WorkOrderWithPartQuantities.QtyInProcess,
            dbo.WorkOrderWithPartQuantities.QtyOrdered,
            dbo.WorkOrderWithPartQuantities.WONumber
            FROM dbo.PartWithQtyInProcess
            INNER JOIN dbo.WorkOrderWithPartQuantities
            ON dbo.PartWithQtyInProcess.WONumber=dbo.WorkOrderWithPartQuantities.WONumber
            ORDER BY DateCreated DESC
            """




# custom_query
custom_query = """


"""
