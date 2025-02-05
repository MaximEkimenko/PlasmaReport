"""Сырые запросы в sigma nest."""
initial_table = "PartWithQtyInProcess"  # основная таблица справочно
joined_table = "WorkOrderWithPartQuantities"  # присоединённая справочно

work_orders_table = "WO"  # таблица с номерами текущих рабочих подрядов (заказов)
program_table = "Program"  # таблица с названиями программ
full_table = "PIP"  # таблица со всеми данными касательно программ


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

programs_name_query = """
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
