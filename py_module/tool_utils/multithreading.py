from multiprocessing.pool import ThreadPool

NUM_THREADS = 8


def perform_sync_tasks(function, inputs: list, dynamic_arg_index: int, args: tuple) -> list:
    curr_thread = 0
    outputs: list = [None]*len(inputs)
    num_inputs: int = len(inputs)
    while curr_thread != num_inputs:
        available_threads = min(NUM_THREADS, num_inputs-curr_thread)

        pool = ThreadPool(available_threads)
        thread_list = [None]*NUM_THREADS

        start = curr_thread
        for i in range(0, available_threads):
            curr_args: list = list(args)
            curr_args[dynamic_arg_index] = inputs[start+i]
            curr_args += [i] # for thread id
            thread_list[i] = pool.apply_async(function, tuple(curr_args))
            curr_thread+=1

        pool.close()
        pool.join()
        for i in range(0, available_threads):
            result = thread_list[i].get()
            outputs[start+i] = result

    return outputs
