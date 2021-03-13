def handle_block_that_has_one_father(self,list_of_fathers,node):
    father = list_of_fathers[0]
    father = Block.create_block_from_tuple(father)
    # check pow{
    target = 2 ** (256 - self.proof_of_work_difficulty)
    input_to_hash = father.as_str() + str(block.proof_of_work)

    hash_result = hashlib.sha256(input_to_hash.encode()).hexdigest()
    if int(hash_result, 16) >= target:  # aka proof of work is not good
        print('invalid pow')
        return AddBlockStatus.INVALID_BLOCK
    # }

    # add the block to the table
    my_id = self.blockchain_table.current_block_id
    my_parent_id = father.id
    my_sequence_number = 0  # TODO
    my_level = father.level + 1
    my_security_number = 0
    block.set_table_parameters(my_id, my_parent_id, my_sequence_number, my_level, my_security_number)
    self.blockchain_table.insert_block(block)
    # }

    # {'
    print(f'cbl {block.level}, {self.blockchain_table.block_to_calc_proof_of_work.level}')
    if block.level > self.blockchain_table.block_to_calc_proof_of_work.level:
        self.blockchain_table.block_to_calc_proof_of_work = block
    # }

    self.blockchain_table.memory_cursor.execute(
        f'''SELECT ID FROM Blockchain WHERE ParentId = {my_parent_id}''')
    list_of_brothers = self.blockchain_table.memory_cursor.fetchall()

    if len(list_of_brothers) == 1:  # aka i am the first son
        """
        here there are two options 
        1: I run and Update both the memory table and the one in the db but i stop when the updating finshed
           on the memory table. it will be faster and more efficient 
        2: I do the same thing but i stop when the table in the db is finished (also the table on memory will finish).
           It will take more time and as the chain keeps growing the time will increase in a liner line
    
        for now i choose option 1 but i am open for change
        """
        current_block = block
        while True:
            command = f'''SELECT * FROM Blockchain WHERE ID = {current_block.parent_id} '''
            self.blockchain_table.memory_cursor.execute(command)
            father_block_list = self.blockchain_table.memory_cursor.fetchall()
            if len(father_block_list) == 0:  # aka  I finished to update the entire memory table
                break
            elif len(father_block_list) == 1:
                father_block = Block.create_block_from_tuple(father_block_list[0])
                self.blockchain_table.increase_block_security_number(father_block.id)
                current_block = father_block
            else:
                raise Exception('block has an unexpected amount of fathers')

        #  check if any blocks has passed the security threshold
        #  and remove any block that has an equal \ lower level the them{

        command = f'''SELECT * FROM Blockchain WHERE SecurityNumber > {self.blockchain_table.calculate_security_number_threshold()} '''
        self.blockchain_table.memory_cursor.execute(command)
        list_of_blocks_that_need_to_be_processed = self.blockchain_table.memory_cursor.fetchall()
        len_of_list_of_blocks_that_need_to_be_processed = len(list_of_blocks_that_need_to_be_processed)
        if len_of_list_of_blocks_that_need_to_be_processed == 0:
            pass
        elif len_of_list_of_blocks_that_need_to_be_processed == 1:
            block_to_process = Block.create_block_from_tuple(list_of_blocks_that_need_to_be_processed[0])
            self.process_block(block_to_process, node)
            self.general_val_table.set_last_level_processed(block_to_process.level)
            # remove blocks that  became irrelevant
            command = f'''SELECT * FROM Blockchain WHERE Level <= {block_to_process.level} '''
            self.blockchain_table.memory_cursor.execute(command)
            list_of_blocks_to_delete = self.blockchain_table.memory_cursor.fetchall()
            list_of_blocks_to_delete = [Block.create_block_from_tuple(block) for block in
                                        list_of_blocks_to_delete]
            for block in list_of_blocks_to_delete:
                # return all the transactions and users that the node uploaded because the have been deleted
                # and need to go back on the list so that the node could try to upload then again{
                if block.uploader_username == self.username:
                    list_of_new_user_as_str = [user.as_str() for user in block.list_of_new_users]
                    list_of_transactions_as_str = [tran.as_str() for tran in block.list_of_transactions]

                    node.list_of_new_users_to_upload.extend(
                        [user for user in node.list_of_new_users_to_upload_waiting_to_be_processed if
                         user.as_str() in list_of_new_user_as_str])

                    node.list_of_transactions_to_make.extend(
                        [tran for tran in node.list_of_transactions_to_make_waiting_to_be_processed if
                         tran.as_str() in list_of_transactions_as_str])
                # }

                print(f"deleting block {block.as_str()}")
            command = f'''DELETE FROM Blockchain WHERE Level <= {block_to_process.level} '''
            self.blockchain_table.memory_cursor.execute(command)
        else:
            print(list_of_blocks_that_need_to_be_processed)

            raise Exception('more then one block has passed the threshold')
        # }
    elif len(list_of_brothers) > 1:  # aka i am not the first son
        pass  # TODO: see if updating the SequenceNumber is relevant
    else:
        raise Exception(f'an unexpected amount of sons {len(list_of_brothers)}')

    # check the orphan list
    for orphan_block in self.blockchain_table.orphans_list:
        if orphan_block.last_block_hash == block.current_block_hash:
            self.blockchain_table.orphans_list.remove(orphan_block)
            self.add_block(orphan_block, node)
    return AddBlockStatus.SUCCESSFUL