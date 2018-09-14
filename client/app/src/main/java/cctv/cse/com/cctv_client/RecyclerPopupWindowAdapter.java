package cctv.cse.com.cctv_client;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import java.util.List;

/**
 * Created by sy081 on 2018-09-14.
 */

public class RecyclerPopupWindowAdapter extends RecyclerView.Adapter<RecyclerPopupWindowAdapter.MyViewHolder> {

    private List<Item> items;
    private int prePosition;
    private static final int TYPE_INACTIVE = 0;
    private static final int TYPE_ACTIVE = 1;

    public RecyclerPopupWindowAdapter(List<Item> items) {
        super();
        prePosition = 0;
        this.items = items;
    }

    @Override
    public int getItemViewType(int position) {
        Item item = items.get(position);
        return item.isActive() ? TYPE_ACTIVE : TYPE_INACTIVE;
    }

    @Override
    public MyViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        int layout = viewType == TYPE_INACTIVE ? R.layout.item_inactive : R.layout.item_active;
        View itemView = LayoutInflater.from(parent.getContext()).inflate(layout, parent, false);
        return new MyViewHolder(itemView, onItemClickListener);
    }

    @Override
    public void onBindViewHolder(MyViewHolder holder, int position) {
        Item item = items.get(position);
        holder.getTimeTV().setText(item.getTitle());
    }

    @Override
    public int getItemCount() {
        return items.size();
    }

    private OnItemClickListener onItemClickListener;

    public void setOnItemClickListener(OnItemClickListener listener) {
        this.onItemClickListener = listener;
    }

    class MyViewHolder extends RecyclerView.ViewHolder implements View.OnClickListener {
        private TextView timeTV;
        private OnItemClickListener mListener;

        public MyViewHolder(View rootView, OnItemClickListener listener) {
            super(rootView);
            this.mListener = listener;
            timeTV = (TextView) rootView.findViewById(R.id.tv_item_time);
            rootView.setOnClickListener(this);
        }

        @Override
        public void onClick(View v) {
            if (mListener != null) {
                mListener.onItemClick(getAdapterPosition());
            }
        }

        public TextView getTimeTV() {
            return timeTV;
        }
    }

    public interface OnItemClickListener {
        void onItemClick(int position);
    }
}