def find_proof_of_work(self):
    self.acquire()
    block = self.block_to_calc_proof_of_work
    self.release()
    while True:
        target = 2 ** (256 - self.proof_of_work_difficulty)
        for nonce in range(MAX_NONCE):
            if nonce % PROOF_OF_WORK_CHECK_BLOCK_FREQUENCY == 0:
                self.acquire()
                if block != self.block_to_calc_proof_of_work:
                    block = self.block_to_calc_proof_of_work.as_str()
                    self.release()
                    break
                self.release()
            input_to_hash = block.as_str() + str(nonce)
            hash_result = hashlib.sha256(input_to_hash.encode()).hexdigest()

            if int(hash_result, 16) < target:
                print(f'\nhash result {hash_result}\n input to hash {input_to_hash}\n')
                self.acquire()
                # build block to upload {
                list_of_transactions_to_make = self.list_of_transactions_to_make[
                                               :max(len(self.list_of_transactions_to_make),
                                                    MAX_LEN_OF_LIST_OF_TRANSACTIONS)]
                list_of_new_users_to_upload = self.list_of_new_users_to_upload[:
                                                                               max(len(
                                                                                   self.list_of_new_users_to_upload),
                                                                                   MAX_LEN_OF_LIST_OF_NEW_USERS)]
                last_block_hash = block.current_block_hash
                self.block_to_upload = Block(self.username, list_of_transactions_to_make,
                                             list_of_new_users_to_upload,
                                             last_block_hash)
                self.block_to_upload.proof_of_work = nonce
                self.release()
                # }