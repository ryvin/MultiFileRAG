try:
    from unstructured.partition.auto import partition
    print('unstructured is installed correctly')
except ImportError as e:
    print(f'Error importing unstructured: {e}')
