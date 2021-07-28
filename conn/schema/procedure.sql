

-- Data exporting was unselected.
-- Dumping structure for procedure db_freknur_loan.sProcActivateWallet
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `db_freknur_loan`.`sProcActivateWallet`(
	IN `MSISDN` VARCHAR(50),
	IN `PASSWD` VARCHAR(50)
)
BEGIN
	-- ====================================================================
	-- .Params.
	-- .@MSISDN.
	-- .@PASSWD.
	-- ====================================================================
	IF(TRIM(MSISDN) <> "") THEN
		-- ====================================================================
		-- .sql statement 1.
		-- ====================================================================	
		SET @STMT_1 = CONCAT("SELECT ",
		                     "COUNT(`MSISDN`) ",
							 "INTO ",
							 "@EXIST ",
							 "FROM ",
							 "`tbl_wallet` ",
							 "WHERE ",
							 "`msisdn` = '",TRIM(MSISDN),"'");
		PREPARE QUERY FROM @STMT_1;
		EXECUTE QUERY;
		DEALLOCATE PREPARE QUERY;
		-- ====================================================================
		-- .sql statement 2.
		-- ====================================================================
		IF(@EXIST = "0") THEN	
			SET @STMT_2 = CONCAT("INSERT ",
			                     "INTO ",
								 "`tbl_wallet` ",
								 "(`uid`,`msisdn`,`password`,`date_created`) ",
								 "VALUES ",
								 "('",uuid_short(),"','",TRIM(MSISDN),"','",TRIM(PASSWD),"','",NOW(),"') ",
								 "ON DUPLICATE KEY ",
								 "UPDATE `date_modified` = '",NOW(),"'");
			PREPARE QUERY FROM @STMT_2;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;
		ELSE
			-- ====================================================================
			-- .output.
			-- ====================================================================
			SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"Already registered"}';
			SELECT @JSON_O AS _JSON;			
		END IF;	
		-- ====================================================================
		-- .output.
		-- ====================================================================
		SET @JSON_O = '{"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Registration successful"}';
		SELECT @JSON_O AS _JSON;				
	ELSE
		-- ====================================================================
		-- .output.
		-- ====================================================================		
		SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"Params:MSISDN|PASSWORD needs to be SET."}';
		SELECT @JSON_O AS _JSON;
	END IF;
		-- ====================================================================
		-- .reset the vars.
		-- ====================================================================
		SET @EXIST  = NULL;
		SET @STMT_1 = NULL;
		SET @STMT_2 = NULL;
		SET @JSON_O = NULL;
		SET MSISDN  = NULL;
		SET PASSWD  = NULL;	
END$$
DELIMITER; //

-- Dumping structure for procedure db_freknur_loan.sProcGenerateID
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `db_freknur_loan`.`sProcGenerateID`(
	OUT `NEW_ID` VARCHAR(10)
)
BEGIN
	-- ====================================================================
	-- .Params.
	-- .@NEW_ID.
	-- ====================================================================

	-- ====================================================================
	-- .unique code generator.
	-- ====================================================================
	SET @STMT_1 = CONCAT("SELECT ",
					     "CONCAT(CHAR(ROUND(RAND()*25)+97), ",
                         "CHAR(ROUND(RAND()*25)+97), ",
	                     "ROUND((RAND()*9)), ",
	                     "CHAR(ROUND(RAND()*25)+97), ",
	                     "CHAR(ROUND(RAND()*25)+97), ",
	                     "CHAR(ROUND(RAND()*25)+97), ",
	                     "ROUND((RAND()*9)), ",
	                     "CHAR(ROUND(RAND()*25)+97), ",
	                     "CHAR(ROUND(RAND()*25)+97), ",
	                     "CHAR(ROUND(RAND()*25)+97)) INTO @UNIQ_ID");
	PREPARE QUERY FROM @STMT_1;
	EXECUTE QUERY;
	DEALLOCATE PREPARE QUERY;
	-- ====================================================================
	-- .output.
	-- ====================================================================		
	SET NEW_ID = @UNIQ_ID;
	-- ====================================================================
	-- .reset vars.
	-- ====================================================================
	SET @STMT_1 = NULL;
	SET @UNIQ_ID = NULL;	
END$$
DELIMITER; //

-- Dumping structure for procedure db_freknur_loan.sProcHasExistingLoan
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `db_freknur_loan`.`sProcHasExistingLoan`(
	IN `MSISDN` VARCHAR(50),
	OUT `OUTPUT` VARCHAR(1)
)
BEGIN
	-- ====================================================================
	-- .Params.
	-- .@MSISDN
	-- .@OUTPUT.
	-- ====================================================================
	IF(TRIM(MSISDN) <> "") THEN
		-- ====================================================================
		-- .sql statement 1.
		-- ====================================================================	
		SET @STMT_1 = CONCAT("SELECT ",
		                     "COUNT(`reference_no`) ",
							 "INTO ",
							 "@LOAN_CNT ",
							 "FROM ",
							 "`tbl_debtor` ",
							 "WHERE ",
							 "`msisdn` = '",TRIM(MSISDN),"' AND `is_repaid` = '0'");
		PREPARE QUERY FROM @STMT_1;
		EXECUTE QUERY;
		DEALLOCATE PREPARE QUERY;
		-- ====================================================================
		-- .get loan count.
		-- ====================================================================
		IF(@LOAN_CNT = "0")THEN
			SET @STMT_2 = CONCAT("SELECT 0 INTO @NO_OF_LOAN");
		ELSE
			SET @STMT_2 = CONCAT("SELECT 1 INTO @NO_OF_LOAN");
		END IF;
		PREPARE QUERY FROM @STMT_2;
		EXECUTE QUERY;
		DEALLOCATE PREPARE QUERY;
		-- ====================================================================
		-- .output.
		-- ====================================================================		
		SET OUTPUT = @NO_OF_LOAN; 	
	END IF;
	-- ====================================================================
	-- .reset the vars.
	-- ====================================================================	
	SET @STMT_1     = NULL;
	SET @STMT_2     = NULL;
	SET @LOAN_CNT   = NULL;
	SET @NO_OF_LOAN = NULL;
	SET MSISDN      = NULL;
END$$
DELIMITER; //

-- Dumping structure for procedure db_freknur_loan.sProcLoanDispatch
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `db_freknur_loan`.`sProcLoanDispatch`(
	IN `REFERENCE_NO` VARCHAR(50),
	IN `MSISDN` VARCHAR(15),
	IN `AMOUNT_REQUESTED` DOUBLE(15,2),
	IN `AMOUNT_DISBURSED` DOUBLE(15,2),
	IN `REPAYMENT_AMOUNT` DOUBLE(15,2),
	IN `INTEREST_AMOUNT` DOUBLE(15,2),
	IN `DURATION_IN_DAYS` VARCHAR(5),
	IN `NOTIFICATION_1` VARCHAR(2)
)
BEGIN
	-- ====================================================================
	-- .Params.
	-- .@REFERENCE_NO.
	-- .@MSISDN.
	-- .@AMOUNT_REQUESTED.
	-- .@AMOUNT_DISBURSED.
	-- .@REPAYMENT_AMOUNT.
	-- .@DURATION_IN_DAYS.
	-- .@NOTIFICATION_1.
	-- ====================================================================
	DECLARE RUNNING_BAL DOUBLE(15,2);
	DECLARE PARTICULARS TEXT;
	DECLARE exit handler FOR SQLEXCEPTION, SQLWARNING
	BEGIN
		ROLLBACK;
		RESIGNAL;
	END;
	-- ====================================================================
	-- .start transaction.
	-- ====================================================================
	START TRANSACTION;
	-- ====================================================================
	-- .valid params.
	-- ====================================================================
	IF(TRIM(REFERENCE_NO) != "" OR TRIM(MSISDN) != "" OR TRIM(AMOUNT_REQUESTED) != "" OR TRIM(AMOUNT_DISBURSED) != "" OR TRIM(REPAYMENT_AMOUNT) != "" OR TRIM(DURATION_IN_DAYS) != "" OR TRIM(NOTIFICATION_1) != "") THEN
		-- ====================================================================
		-- .sql statement 1.
		-- ====================================================================	
		SET @STMT_0 = CONCAT("SELECT ",
		                     "COUNT(`uid`),`balance` ",
							 "INTO ",
							 "@HAS_ACCOUNT,@BALANCE ",
							 "FROM ",
							 "`tbl_wallet` ",
							 "WHERE ",
							 "`msisdn` = '",TRIM(MSISDN),"'");
		PREPARE QUERY FROM @STMT_0;
		EXECUTE QUERY;
		DEALLOCATE PREPARE QUERY;
		IF(@HAS_ACCOUNT > "0") THEN
			-- ====================================================================
			-- .calc loan repayment date.
			-- ====================================================================			
			SET @REPAYMENT_DATE = DATE_ADD(NOW(), INTERVAL (DURATION_IN_DAYS * 24) HOUR);
			-- ====================================================================
			-- .calc notifaction date.
			-- ====================================================================			
			SET @NOTIFICATION_DATE = DATE_ADD(@REPAYMENT_DATE, INTERVAL (NOTIFICATION_1 * -1) HOUR);	
			-- ====================================================================
			-- .sql statement 2.
			-- ====================================================================
			SET @STMT_1 = CONCAT("INSERT ",
			                     "INTO ",
			                     "`tbl_debtor` ",
			                     "(`reference_no`,`msisdn`,`amount_requested`,`amount_disbursed`,`repayment_amount`,`interest_amount`,`date_created`,`expected_repayment_date`,`repayment_date`,`next_notification_date`) ",
			                     "VALUES ",
			                     "('",TRIM(REFERENCE_NO),"','",TRIM(MSISDN),"','",TRIM(AMOUNT_REQUESTED),"','",TRIM(AMOUNT_DISBURSED),"','",TRIM(REPAYMENT_AMOUNT),"','",TRIM(INTEREST_AMOUNT),"','",NOW(),"','",@REPAYMENT_DATE,"','",@REPAYMENT_DATE,"','",@NOTIFICATION_DATE,"') ",
			                     "ON DUPLICATE KEY ",
			                     "UPDATE `date_modified` = '",NOW(),"'");	
			PREPARE QUERY FROM @STMT_1;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;
			-- ====================================================================
			-- .sql statement 3.
			-- ====================================================================
			SET @STMT_2 = CONCAT("INSERT ",
			                     "INTO ",
							     "`tb_wallet_transaction` ",
							     "(`reference_no`,`msisdn`,`cr`,`balance`,`date_created`) ",
							     "VALUES ",
								 "('",TRIM(REFERENCE_NO),"','",TRIM(MSISDN),"','",TRIM(AMOUNT_DISBURSED),"','",TRIM(AMOUNT_DISBURSED),"','",NOW(),"')");
			PREPARE QUERY FROM @STMT_2;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;
			-- ====================================================================
			-- .calc running balance.
			-- ====================================================================
			SET RUNNING_BAL = (@BALANCE + AMOUNT_DISBURSED);
			-- ====================================================================
			-- .sql statement 4.
			-- ====================================================================
			SET @STMT_3 = CONCAT("UPDATE ",
			                     "`tbl_wallet` ",
							     "SET ",
								 "`balance` = '",TRIM(RUNNING_BAL),"', `date_modified` = '",NOW(),"' ",
								 "WHERE ",
							     "`msisdn` = '",TRIM(MSISDN),"'");
			PREPARE QUERY FROM @STMT_3;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;
			-- ====================================================================
			-- .set particulars.
			-- ====================================================================
			SET PARTICULARS = 'MONEY MOVED TO CLIENT WALLET A/C.';			
			-- ====================================================================
			-- .sql statement 5.
			-- ====================================================================
			SET @STMT_4 = CONCAT("INSERT ",
			                     "INTO ",
								 "`tbl_transaction` ",
								 "(`account_code`,`reference_no`,`msisdn`,`cr`,`dr`,`balance`,`narration`,`date_created`) ",
								 "VALUES ",
								 "('0','",TRIM(REFERENCE_NO),"','",TRIM(MSISDN),"','",TRIM(AMOUNT_DISBURSED),"','0.00','",TRIM(RUNNING_BAL),"','",PARTICULARS,"','",NOW(),"')");
			PREPARE QUERY FROM @STMT_4;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;			
			-- ====================================================================
			-- .sql statement 6.
			-- ====================================================================
			SET @STMT_5 = CONCAT("UPDATE ",
			                     "`tbl_loan_payout` ",
								 "SET ",
								 "`is_processed` = '1', `date_modified` = '",NOW(),"' ",
								 "WHERE ",
								 "`reference_no` = '",TRIM(REFERENCE_NO),"' AND `msisdn` = '",TRIM(MSISDN),"'");	   
			PREPARE QUERY FROM @STMT_5;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;
			-- ====================================================================
			-- .output.
			-- ====================================================================	
			SET @JSON_O = CONCAT('{"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"LOAN DISPATCHED TO ACCOUNT:',MSISDN,'"}');
			SELECT @JSON_O AS _JSON;									
		ELSE
			-- ====================================================================
			-- .output.
			-- ====================================================================	
			SET @JSON_O = CONCAT('{"ERROR":"1","RESULT":"FAIL","MESSAGE":"ACCOUNT DOES NOT EXIST:',MSISDN,'"}');
			SELECT @JSON_O AS _JSON;			
		END IF;
	ELSE
		-- ====================================================================
		-- .output.
		-- ====================================================================	
		SET @JSON_O = '{"ERROR":"0","RESULT":"FAIL","MESSAGE":"Params:REFERENCE_NO|MSISDN|AMOUNT_REQUESTED|AMOUNT_DISBURSED|REPAYMENT_AMOUNT needs to be SET."}';
		SELECT @JSON_O AS _JSON;	
	END IF;
	-- ====================================================================
	-- .commit transaction.
	-- ====================================================================
	COMMIT;
	-- ====================================================================
	-- .reset the vars.
	-- ====================================================================
	SET @STMT_1 = NULL;
	SET @STMT_2 = NULL;
	SET @STMT_3 = NULL;
	SET @STMT_4 = NULL;
	SET @JSON_O = NULL;
	SET @BALANCE = NULL;
	SET @HAS_ACCOUNT = NULL;
	SET @REPAYMENT_DATE = NULL;
	SET @NOTIFICATION_DATE = NULL;
	SET MSISDN  = NULL;
	SET PARTICULARS = NULL;
	SET RUNNING_BAL = NULL;
	SET REFERENCE_NO  = NULL;
	SET AMOUNT_REQUESTED = NULL;
	SET AMOUNT_DISBURSED = NULL;
	SET REPAYMENT_AMOUNT = NULL;
	SET DURATION_IN_DAYS = NULL;
	SET NOTIFICATION_1 = NULL;
END$$
DELIMITER; //

-- Dumping structure for procedure db_freknur_loan.sProcLoanRequest
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `db_freknur_loan`.`sProcLoanRequest`(
	IN `MSISDN` VARCHAR(50),
	IN `AMOUNT` VARCHAR(50)
)
BEGIN
	-- ====================================================================
	-- .Params.
	-- .@MSISDN
	-- .@AMOUNT.
	-- ====================================================================
	IF(TRIM(MSISDN) <> "" AND TRIM(AMOUNT) <> "") THEN
		-- ====================================================================
		-- .sql statement 1.
		-- ====================================================================	
		SET @STMT_1 = CONCAT("SELECT ",
		                     "COUNT(`msisdn`) ",
							 "INTO ",
							 "@REQUEST_CNT ",
							 "FROM ",
							 "`tbl_loan_request` ",
							 "WHERE ",
							 "`msisdn` ='",TRIM(MSISDN),"' AND `is_processed` = '0'");
		PREPARE QUERY FROM @STMT_1;
		EXECUTE QUERY;
		DEALLOCATE PREPARE QUERY;
		IF(@REQUEST_CNT = 0) THEN
			-- ====================================================================
			-- .stored proc call to check for existing loan.
			-- ====================================================================
			CALL `sProcHasExistingLoan`(MSISDN,@HAS_LOAN);
			-- ====================================================================
			-- .do have a loan?
			-- ====================================================================
			IF(@HAS_LOAN = "1")THEN
				-- ====================================================================
				-- .output.
				-- ====================================================================
				SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have an existing loan."}';
				SELECT @JSON_O AS _JSON;			
			ELSE
				-- ====================================================================
				-- .stored proc call.
				-- ====================================================================
				CALL `sProcGenerateID`(@REF_NUM);	
				-- ====================================================================
				-- .sql statement 2.
				-- ====================================================================	
				SET @STMT_2 = CONCAT("INSERT ",
				                     "INTO ",
									 "`tbl_loan_request` ",
									 "(`msisdn`,`reference_no`,`amount`,`requested_by`,`date_created`) ",
									 "VALUES ",
									 "('",TRIM(MSISDN),"','",UCASE(@REF_NUM),"','",TRIM(AMOUNT),"','",TRIM(MSISDN),"','",NOW(),"') ",
									 "ON DUPLICATE KEY ",
									 "UPDATE `date_modified` = NOW()");
				PREPARE QUERY FROM @STMT_2;
				EXECUTE QUERY;
				DEALLOCATE PREPARE QUERY;
				-- ====================================================================
				-- .output.
				-- ====================================================================
				SET @JSON_O = '{"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Loan request was successful."}';
				SELECT @JSON_O AS _JSON;
			END IF;
		ELSE
			-- ====================================================================
			-- .output.
			-- ====================================================================
			SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have a pending loan request."}';
			SELECT @JSON_O AS _JSON;					
		END IF;
	ELSE
		-- ====================================================================
		-- .output.
		-- ====================================================================	
		SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"Param: MSISDN|AMOUNT needs to be SET."}';
		SELECT @JSON_O AS _JSON;
	END IF;
		-- ====================================================================
		-- .reset the vars.
		-- ====================================================================
		SET @STMT_1      = NULL;
		SET @STMT_2      = NULL;
		SET @JSON_O      = NULL;
		SET @REF_NUM     = NULL;
		SET @HAS_LOAN    = NULL;		
		SET @REQUEST_CNT = NULL;
		SET MSISDN       = NULL;
		SET AMOUNT       = NULL;
END$$
DELIMITER; //

-- Dumping structure for procedure db_freknur_loan.sProcLogLoanFee
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `db_freknur_loan`.`sProcLogLoanFee`(
	IN `MSISDN` VARCHAR(50),
	IN `REFERENCE_NO` VARCHAR(50),
	IN `HANDLING_FEE` DOUBLE(15,2),
	IN `ACCOUNT_NAME` VARCHAR(15)
)
BEGIN
	-- ====================================================================
	-- .Params.
	-- .@AMOUNT.
	-- .@MSISDN.
	-- .@REFERENCE_NO.
	-- .@HANDLING_FEE.
	-- .@ACCOUNT_NAME.
	-- ====================================================================	
	DECLARE PARTICULARS TEXT;
	DECLARE RUNNING_BAL DOUBLE(15,2);
	IF(TRIM(MSISDN) != "" OR TRIM(REFERENCE_NO) != "" OR TRIM(HANDLING_FEE) != "" OR TRIM(ACCOUNT_NAME) != "") THEN
		-- ====================================================================
		-- .sql statement 1.
		-- ====================================================================
		SET @STMT_0 = CONCAT("SELECT ",
		                     "COUNT(`uid`) ",
							 "INTO ",
							 "@HAS_ACCOUNT ",
							 "FROM ",
							 "`tbl_wallet` ",
							 "WHERE ",
							 "`msisdn` = '",TRIM(MSISDN),"'");
		PREPARE QUERY FROM @STMT_0;
		EXECUTE QUERY;
		DEALLOCATE PREPARE QUERY;
		-- ====================================================================
		-- .has a wallet a/c?
		-- ====================================================================		
		IF(@HAS_ACCOUNT > "0")THEN	
			-- ====================================================================
			-- .sql statement 2.
			-- ====================================================================	
			SET @STMT_1 = CONCAT("SELECT ",
			                     "`account_code`,`account_name`,`balance` ",
			                     "INTO ",
			                     "@ACC_CODE,@ACC_NAME,@BALANCE ",
								 "FROM ",
								 "`tbl_account` ",
								 "WHERE ",
								 "`account_name` = '",TRIM(ACCOUNT_NAME),"'"); 
			PREPARE QUERY FROM @STMT_1;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;	
			-- ====================================================================
			-- .set particulars.
			-- ====================================================================
			SET PARTICULARS = "LOAN HANDLING FEES EARNED.";
			-- ====================================================================
			-- .calc running bal.
			-- ====================================================================	
			SET RUNNING_BAL = (@BALANCE + HANDLING_FEE);	
			-- ====================================================================
			-- .sql statement 3.
			-- ====================================================================
			SET @STMT_2 = CONCAT("INSERT ",
			                     "INTO ",
								 "`tbl_transaction` ",
								 "(`account_code`,`reference_no`,`msisdn`,`cr`,`dr`,`balance`,`narration`,`date_created`) ",
								 "VALUES ",
								 "('",@ACC_CODE,"','",TRIM(REFERENCE_NO),"','",TRIM(MSISDN),"','",TRIM(HANDLING_FEE),"','0.00','",TRIM(RUNNING_BAL),"','",PARTICULARS,"','",NOW(),"')");
			PREPARE QUERY FROM @STMT_2;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;
			-- ====================================================================
			-- .sql statement 4.
			-- ====================================================================											
			SET @STMT_3 = CONCAT("UPDATE ",
			                     "`tbl_account` ",
								 "SET ",
								 "`balance` = '",RUNNING_BAL,"' ",
								 "WHERE ",
								 "`account_code` ='",@ACC_CODE,"'");
			PREPARE QUERY FROM @STMT_3;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;
			-- ====================================================================
			-- .output.
			-- ====================================================================		
			SET @JSON_O = '{"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Movement complete."}';
			SELECT @JSON_O AS _JSON;
		ELSE
			-- ====================================================================
			-- .output.
			-- ====================================================================		
			SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"A/C does not exist."}';
			SELECT @JSON_O AS _JSON;		
		END IF;
	ELSE
		-- ====================================================================
		-- .output.
		-- ====================================================================		
		SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"Params:MSISDN|REFERENCE_NO|HANDLING_FEE|ACCOUNT_NAME needs to be SET."}';
		SELECT @JSON_O AS _JSON;
	END IF;
	-- ====================================================================
	-- .reset the vars.
	-- ====================================================================
	SET @STMT_1 = NULL;
	SET @STMT_2 = NULL;
	SET @STMT_3 = NULL;
	SET @JSON_O = NULL;
	SET @BALANCE  = NULL;
	SET @ACC_CODE = NULL;
	SET @ACC_NAME = NULL;
	SET @HAS_ACCOUNT = NULL;	
	SET MSISDN = NULL;
	SET PARTICULARS = NULL;
	SET RUNNING_BAL = NULL;
	SET REFERENCE_NO = NULL;
	SET ACCOUNT_NAME = NULL;
END$$
DELIMITER; //

-- Dumping structure for procedure db_freknur_loan.sProcLogTransactions
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `db_freknur_loan`.`sProcLogTransactions`(
	IN `AMOUNT` DOUBLE(15,2),
	IN `MSISDN` VARCHAR(15),
	IN `REFERENCE_NO` VARCHAR(50),
	IN `ACCOUNT_NAME` VARCHAR(15),
	IN `TRANS_TYPE` VARCHAR(5)
)
BEGIN
	-- ====================================================================
	-- .Params.
	-- .@AMOUNT.
	-- .@MSISDN.
	-- .@REFERENCE_NO.
	-- .@ACCOUNT_NAME.
	-- .@TRANS_TYPE.
	-- ====================================================================	
	DECLARE PARTICULARS TEXT;
	DECLARE RUNNING_BAL DOUBLE(15,2);
	-- ====================================================================
	-- .params checked.
	-- ====================================================================	
	IF(TRIM(AMOUNT) != "" OR TRIM(MSISDN) != "" OR TRIM(REFERENCE_NO) != "" OR TRIM(ACCOUNT_NAME) != "" OR TRIM(TRANS_TYPE) != "") THEN
		-- ====================================================================
		-- .sql statement 1.
		-- ====================================================================
		SET @STMT_0 = CONCAT("SELECT ",
		                     "COUNT(`uid`) ",
							 "INTO ",
							 "@HAS_ACCOUNT ",
							 "FROM ",
							 "`tbl_wallet` ",
							 "WHERE ",
							 "`msisdn` = '",TRIM(MSISDN),"'");
		PREPARE QUERY FROM @STMT_0;
		EXECUTE QUERY;
		DEALLOCATE PREPARE QUERY;
		-- ====================================================================
		-- .has a wallet a/c?
		-- ====================================================================		
		IF(@HAS_ACCOUNT > "0")THEN		
			-- ====================================================================
			-- .sql statement 2.
			-- ====================================================================	
			SET @STMT_1 = CONCAT("SELECT ",
			                     "`account_code`,`account_name`,`balance` ",
			                     "INTO ",
								 "@ACC_CODE,@ACC_NAME,@BALANCE ",
								 "FROM ",
								 "`tbl_account` ",
								 "WHERE ",
								 "`account_name` = '",TRIM(ACCOUNT_NAME),"'"); 
			PREPARE QUERY FROM @STMT_1;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;
			-- ====================================================================
			-- .transaction type.
			-- ====================================================================			
			IF(UCASE(TRANS_TYPE) = "DR") THEN
				SET PARTICULARS = "MONEY MOVEMENT OUT OF UTY.";
				-- ====================================================================
				-- .calc running bal.
				-- ====================================================================	
				SET RUNNING_BAL = (@BALANCE - AMOUNT);		
				-- ====================================================================
				-- .sql statement 3.
				-- ====================================================================				
				SET @STMT_2 = CONCAT("INSERT ",
				                     "INTO ",
									 "`tbl_transaction` ",
									 "(`account_code`,`reference_no`,`msisdn`,`cr`,`dr`,`balance`,`narration`,`date_created`) ",
									 "VALUES ",
									 "('",@ACC_CODE,"','",TRIM(REFERENCE_NO),"','",TRIM(MSISDN),"','0.00','",TRIM(AMOUNT),"','",TRIM(RUNNING_BAL),"','",PARTICULARS,"','",NOW(),"')");
				-- ====================================================================
				-- .sql statement 4.
				-- ====================================================================											
				SET @STMT_3 = CONCAT("UPDATE ",
				                     "`tbl_account` ",
									 "SET ",
									 "`balance` = '",RUNNING_BAL,"',`date_modified` = '",NOW(),"' ",
									 "WHERE ",
									 "`account_code` ='",@ACC_CODE,"'");																																			
			ELSE
				SET PARTICULARS = "MONEY MOVEMENT INTO DEP.";
				-- ====================================================================
				-- .calc running bal.
				-- ====================================================================	
				SET RUNNING_BAL = (@BALANCE + AMOUNT);	
				-- ====================================================================
				-- .sql statement 3.
				-- ====================================================================		
				SET @STMT_2 = CONCAT("INSERT ",
				                     "INTO ",
									 "`tbl_transaction` ",
									 "(`account_code`,`reference_no`,`msisdn`,`cr`,`dr`,`balance`,`narration`,`date_created`) ",
									 "VALUES ",
									 "('",@ACC_CODE,"','",TRIM(REFERENCE_NO),"','",TRIM(MSISDN),"','",TRIM(HANDLING_FEE),"','0.00','",RUNNING_BAL,"','",PARTICULARS,"','",NOW(),"')");
				-- ====================================================================
				-- .sql statement 4.
				-- ====================================================================											
				SET @STMT_3 = CONCAT("UPDATE ",
				                     "`tbl_account` ",
									 "SET ",
									 "`balance` = '",RUNNING_BAL,"',`date_modified` = '",NOW(),"' ",
									 "WHERE ",
									 "`account_code` ='",@ACC_CODE,"'");																				
			END IF;
			-- ====================================================================
			-- .commit stmt 3.
			-- ====================================================================		
			PREPARE QUERY FROM @STMT_2;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;
			-- ====================================================================
			-- .commit stmt 4.
			-- ====================================================================		
			PREPARE QUERY FROM @STMT_3;
			EXECUTE QUERY;
			DEALLOCATE PREPARE QUERY;		
			-- ====================================================================
			-- .output.
			-- ====================================================================		
			SET @JSON_O = '{"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Movement complete."}';
			SELECT @JSON_O AS _JSON;	
		ELSE
			-- ====================================================================
			-- .output.
			-- ====================================================================		
			SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"Params:AMOUNT|MSISDN|REFERENCE_NO|ACCOUNT_NAME|TRANS_TYPE needs to be SET."}';
			SELECT @JSON_O AS _JSON;
		END IF;
	ELSE
		-- ====================================================================
		-- .output.
		-- ====================================================================		
		SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"A/C does not exist."}';
		SELECT @JSON_O AS _JSON;
	END IF;
	-- ====================================================================
	-- .reset the vars.
	-- ====================================================================
	SET @STMT_1 = NULL;
	SET @STMT_2 = NULL;
	SET @STMT_3 = NULL;
	SET @JSON_O = NULL;
	SET @BALANCE  = NULL;
	SET @ACC_CODE = NULL;
	SET @ACC_NAME = NULL;	
	SET AMOUNT = NULL;
	SET MSISDN = NULL;
	SET REFERENCE_NO = NULL;
	SET ACCOUNT_NAME = NULL;
	SET TRANS_TYPE = NULL;
	SET PARTICULARS = NULL;
	SET RUNNING_BAL = NULL;
END$$
DELIMITER; //

-- Dumping structure for procedure db_freknur_loan.sProcQueueLoan
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `db_freknur_loan`.`sProcQueueLoan`(
	IN `REFERENCE_NO` VARCHAR(50),
	IN `MSISDN` VARCHAR(15),
	IN `AMOUNT` DOUBLE(15,2),
	IN `APPROVED_BY` VARCHAR(50)
)
BEGIN
	-- ====================================================================
	-- .Params.
	-- .@MSISDN.
	-- .@REFERENCE_NO.
	-- .@AMOUNT.
	-- .@APPROVED_BY.
	-- ====================================================================
IF(TRIM(REFERENCE_NO) != "" OR TRIM(MSISDN) != "" OR TRIM(AMOUNT) != "" OR TRIM(APPROVED_BY) != "") THEN
	-- ====================================================================
	-- .sql statement 1.
	-- ====================================================================	
	SET @STMT_1 = CONCAT("INSERT INTO ",
						 "`tbl_loan_payout` ",
						 "(`reference_no`,`msisdn`,`amount`,`date_created`,`approved_by`) ",
						 "VALUES ",
						 "('",TRIM(REFERENCE_NO),"','",TRIM(MSISDN),"','",TRIM(AMOUNT),"','",NOW(),"','",TRIM(APPROVED_BY),"') ",
						 "ON DUPLICATE KEY UPDATE ",
						 "`date_modified` = '",NOW(),"'");                    
	PREPARE QUERY FROM @STMT_1;
	EXECUTE QUERY;
	DEALLOCATE PREPARE QUERY;
	-- ====================================================================
	-- .sql statement 2.
	-- ====================================================================	
	SET @STMT_2 = CONCAT("UPDATE ",
	                     "`tbl_loan_request` ",
						 "SET ",
						 "`is_processed` = 1 ",
						 "WHERE ",
						 "`reference_no` = '",TRIM(REFERENCE_NO),"' AND `msisdn` = '",TRIM(MSISDN),"'");	                     
	PREPARE QUERY FROM @STMT_2;
	EXECUTE QUERY;
	DEALLOCATE PREPARE QUERY;	
	-- ====================================================================
	-- .output.
	-- ====================================================================	
	SET @JSON_O = '{"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Operation successful."}';
	SELECT @JSON_O AS _JSON;		
ELSE
	-- ====================================================================
	-- .output.
	-- ====================================================================	
	SET @JSON_O = '{"ERROR":"1","RESULT":"FAIL","MESSAGE":"Params:REFERENCE_NO|MSISDN|AMOUNT|APPROVED_BY needs to be SET."}';
	SELECT @JSON_O AS _JSON;
END IF;
	-- ====================================================================
	-- .reset the vars.
	-- ====================================================================
	SET @STMT_1      = NULL;
	SET @STMT_2      = NULL;
	SET @JSON_O      = NULL;
	SET REFERENCE_NO = NULL;
	SET MSISDN       = NULL;
	SET AMOUNT       = NULL;
	SET APPROVED_BY  = NULL;
END$$
DELIMITER; //

