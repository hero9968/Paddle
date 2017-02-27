import numpy
import paddle.v2 as paddle


def main():
    paddle.init(use_gpu=False, trainer_count=1)

    # define network topology
    images = paddle.layer.data(
        name='pixel', type=paddle.data_type.dense_vector(784))
    label = paddle.layer.data(
        name='label', type=paddle.data_type.integer_value(10))
    hidden1 = paddle.layer.fc(input=images, size=200)
    hidden2 = paddle.layer.fc(input=hidden1, size=200)
    inference = paddle.layer.fc(input=hidden2,
                                size=10,
                                act=paddle.activation.Softmax())
    cost = paddle.layer.classification_cost(input=inference, label=label)

    parameters = paddle.parameters.create(cost)
    for param_name in parameters.keys():
        array = parameters.get(param_name)
        array[:] = numpy.random.uniform(low=-1.0, high=1.0, size=array.shape)
        parameters.set(parameter_name=param_name, value=array)

    adam_optimizer = paddle.optimizer.Adam(learning_rate=0.01)

    def event_handler(event):
        if isinstance(event, paddle.event.EndIteration):
            para = parameters.get('___fc_2__.w0')
            print "Pass %d, Batch %d, Cost %f, Weight Mean Of Fc 2 is %f" % (
                event.pass_id, event.batch_id, event.cost, para.mean())

        else:
            pass

    trainer = paddle.trainer.SGD(update_equation=adam_optimizer)

    reader = paddle.reader.batched(
        paddle.reader.shuffle(
            paddle.dataset.mnist.train_creator(), buf_size=8192),
        batch_size=32)

    trainer.train(
        train_reader=paddle.reader.batched(
            paddle.reader.shuffle(paddle.dataset.mnist.train_creator(),
                                  buf_size=8192), batch_size=32),
        topology=cost,
        parameters=parameters,
        event_handler=event_handler,
        data_types=[  # data_types will be removed, It should be in
            # network topology
            ('pixel', images.type),
            ('label', label.type)],
        reader_dict={'pixel': 0, 'label': 1}
    )


if __name__ == '__main__':
    main()
